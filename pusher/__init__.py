import os
import time
import hmac
import json
import hashlib
import urllib
import re
import requests

__version__ = '0.10'

HOST    = 'api.pusherapp.com'
PORT    = 80
APP_ID  = None
KEY     = None
SECRET  = None

CHANNEL_NAME_RE = re.compile('^[-a-zA-Z0-9_=@,.;]+$')
APP_ID_RE       = re.compile('^[0-9]+$')


def _url2options(url):
    assert url.startswith('http://'), "invalid URL"
    url = url[7:]
    key, url = url.split(':', 1)
    secret, url = url.split('@', 1)
    host, url = url.split('/', 1)
    url, app_id = url.split('/', 1)
    return {'key': key, 'secret': secret, 'host': host, 'app_id': app_id}


def pusher_from_url(url=None):
    url = url or os.environ['PUSHER_URL']
    return Pusher(**_url2options(url))


class AuthenticationError(Exception):
    pass

class NotFoundError(Exception):
    pass

class AppDisabledOrMessageQuotaError(Exception):
    pass

class UnexpectedReturnStatusError(Exception):
    pass


class Pusher(object):
    def __init__(self, app_id=None, key=None, secret=None, host=None, port=None, encoder=None):
        self.app_id = str(app_id or APP_ID)
        if not APP_ID_RE.match(self.app_id):
            raise NameError("Invalid app id")
        self.key = key or KEY
        self.secret = secret or SECRET
        self.host = host or HOST
        self.port = port or PORT
        self.protocol = self.port == 443 and 'https' or 'http'
        self.encoder = encoder
        self._channels = {}

    def __getitem__(self, key):
        if not self._channels.has_key(key):
            return self._make_channel(key)
        return self._channels[key]

    def _make_channel(self, name):
        self._channels[name] = channel_type(name, self)
        return self._channels[name]

    def webhook(self, request_body, header_key, header_signature):
        return WebHook(self, request_body, header_key, header_signature)

    def django_webhook(self, request):
        return DjangoWebHook(self, request)


class Channel(object):
    def __init__(self, name, pusher):
        self.pusher = pusher
        self.name = str(name)
        if not CHANNEL_NAME_RE.match(self.name):
            raise NameError("Invalid channel id: %s" % self.name)
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, urllib.quote(self.name))

    def _get_auth_signature(self, path, params):
        """Get an auth_signature to add to the params

        A hash of the string made up of the lowercased, alphabetized, keys and
        their corresponding values
        via http://pusher.com/docs/rest_api#auth-signature
        """
        print params
        sorted_qs_items = [("%s=%s" % (key.lower(), params[key])) for key in sorted(params.keys())]
        print sorted_qs_items
        query_string = "&".join(sorted_qs_items)
        string_to_sign = "POST\n%s\n%s" % (path, query_string)
        return hmac.new(self.pusher.secret, string_to_sign, hashlib.sha256).hexdigest()

    def _compose_querystring(self, json_data, socket_id, **params):
        hasher = hashlib.md5()
        hasher.update(json_data)
        hash_str = hasher.hexdigest()
        params.update({
            'auth_key': self.pusher.key,
            'auth_timestamp': int(time.time()),
            'auth_version': '1.0',
            'body_md5': hash_str,
        })
        if socket_id:
            params['socket_id'] = unicode(socket_id)
        params['auth_signature'] = self._get_auth_signature(self.path, params)
        return urllib.urlencode(params)

    def _get_url(self, json_data, socket_id, **extra_params):
        query_string = self._compose_querystring(json_data, socket_id, **extra_params)
        return "%s://%s%s?%s" % (self.pusher.protocol,
                                 self.pusher.host,
                                 self.path,
                                 query_string)

    def _send_request(self, url, data_string, timeout=None):
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=data_string, headers=headers, timeout=timeout)
        return response.status_code, response.content

    def trigger(self, event_name, data={}, socket_id=None, timeout=None):
        json_data = json.dumps(data, cls=self.pusher.encoder)
        url = self._get_url(json_data, socket_id, name=event_name)
        status, resp_content = self._send_request(url, json_data, timeout=timeout)
        if status == 202:
            return True
        elif status == 401:
            raise AuthenticationError("Status: 401; Message: %s" % resp_content)
        elif status == 404:
            raise NotFoundError("Status: 404; Message: %s" % resp_content)
        elif status == 403:
            raise AppDisabledOrMessageQuotaError("Status: 403; Message: %s" % resp_content)
        else:
            raise UnexpectedReturnStatusError("Status: %s; Message: %s" % (status, resp_content))

    def _authentication_string(self, socket_id, custom_string=None):
      if not socket_id:
          raise Exception("Invalid socket_id")
      string_to_sign = "%s:%s" % (socket_id, self.name)
      if custom_string:
        string_to_sign += ":%s" % custom_string
      signature = hmac.new(self.pusher.secret, string_to_sign, hashlib.sha256).hexdigest()
      return "%s:%s" % (self.pusher.key,signature)

    def authenticate(self, socket_id, custom_data=None):
        if custom_data:
            custom_data = json.dumps(custom_data, cls=self.pusher.encoder)
        auth = self._authentication_string(socket_id, custom_data)
        r = {'auth': auth}
        if custom_data:
            r['channel_data'] = custom_data
        return r


class GoogleAppEngineChannel(Channel):
    def _send_request(self, url, data_string):
        from google.appengine.api import urlfetch
        response = urlfetch.fetch(
            url=url,
            payload=data_string,
            method=urlfetch.POST,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code, response.content


# App Engine NDB channel, outer try import/except as it uses decorator
try:
    from google.appengine.ext import ndb

    class GaeNdbChannel(GoogleAppEngineChannel):
        @ndb.tasklet
        def trigger_async(self, event_name, data=None, socket_id=None):
            """Async trigger that in turn calls _send_request_async"""
            if data is None:
                data = {}
            json_data = json.dumps(data)
            url = self._get_url(json_data, socket_id, name=event_name)
            status = yield self._send_request_async(url, json_data)
            if status == 202:
                raise ndb.Return(True)
            elif status == 401:
                raise AuthenticationError
            elif status == 404:
                raise NotFoundError
            else:
                raise Exception("Unexpected return status %s" % status)

        @ndb.tasklet
        def _send_request_async(self, url, data_string):
            """Send request and yield while waiting for future result"""
            ctx = ndb.get_context()
            secure = (self.pusher.protocol == 'https')
            result = yield ctx.urlfetch(
                url=url,
                payload=data_string,
                method='POST',
                headers={'Content-Type': 'application/json'},
                validate_certificate=secure,
            )
            raise ndb.Return(result.status_code)
except ImportError:
    pass


class TornadoChannel(Channel):
    def trigger(self, event, data={}, socket_id=None, callback=None, timeout=None):
        self.callback = callback
        return super(TornadoChannel, self).trigger(event, data, socket_id, timeout=timeout)

    def _send_request(self, url, data_string, timeout=None):
        import tornado.httpclient
        request = tornado.httpclient.HTTPRequest(url,
                                                 method='POST',
                                                 body=data_string,
                                                 request_timeout=timeout)
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, callback=self.callback)
        # Returning 202 to avoid Channel errors. Actual error handling takes place in callback.
        return 202, ""


class WebHook(object):
    def __init__(self, pusher, request_body, header_key, header_signature):
        self.pusher = pusher
        self.request_body = request_body
        self.data = json.loads(request_body)
        self.header_key = header_key
        self.header_signature = header_signature

    def valid(self):
        if self.header_key != self.pusher.key:
            return False
        signature = hmac.new(self.pusher.secret, self.request_body, hashlib.sha256).hexdigest()
        return self.header_signature == signature

    def events(self):
        return self.data['events']

    def time(self):
        # TODO: convert this to a native datetime
        return self.data['time_ms']


class DjangoWebHook(WebHook):
    def __init__(self, pusher, request):
        header_key = request.META.get('HTTP_X_PUSHER_KEY')
        header_signature = request.META.get('HTTP_X_PUSHER_SIGNATURE')
        super(DjangoWebHook, self).__init__(pusher, request.body, header_key, header_signature)

channel_type = Channel
