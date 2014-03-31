import os
import time
import hmac
import json
import hashlib
import urllib
import re
import requests

__version__ = '0.10.1'

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

    def _make_channel(self, name):
        self._channels[name] = channel_type(name, self)
        return self._channels[name]

    def __getitem__(self, key):
        if not self._channels.has_key(key):
            return self._make_channel(key)
        return self._channels[key]

    def _get_auth_signature(self, request_type, path, params):
        """Get an auth_signature to add to the params

        A hash of the string made up of the lowercased, alphabetized, keys and
        their corresponding values
        via http://pusher.com/docs/rest_api#auth-signature
        """
        sorted_qs_items = [("%s=%s" % (key.lower(), params[key])) for key in sorted(params.keys())]
        query_string = "&".join(sorted_qs_items)
        string_to_sign = "%s\n%s\n%s" % (request_type, path, query_string)
        return hmac.new(self.secret, string_to_sign, hashlib.sha256).hexdigest()

    def _compose_querystring(self, path, request_type, json_data=None, socket_id=None, **params):
        params.update({
            'auth_key': self.key,
            'auth_timestamp': int(time.time()),
            'auth_version': '1.0',
        })
        if json_data is not None:
            hasher = hashlib.md5()
            hasher.update(json_data)
            hash_str = hasher.hexdigest()
            params['body_md5'] = hash_str
        if socket_id:
            params['socket_id'] = unicode(socket_id)
        params['auth_signature'] = self._get_auth_signature(request_type, path, params)
        return urllib.urlencode(params)

    def _get_url(self, path, request_type, json_data=None, socket_id=None, **params):
        query_string = self._compose_querystring(path, request_type, json_data, socket_id, **params)
        return "%s://%s%s?%s" % (self.protocol,
                                 self.host,
                                 path,
                                 query_string)

    def send_request(self, url, request_type, data=None, timeout=None):
        headers = {'Content-Type': 'application/json'}
        func = getattr(requests, request_type.lower())
        response = func(url, data=data, headers=headers, timeout=timeout)
        return response.status_code, response.content

    def get_channels(self, filter_by_prefix=None, info=None):
        """TODO: implement this, returning stub data for now

        http://pusher.com/docs/rest_api
        """
        return {
            'channels': {
                'presence-foobar': {
                    'user_count': 42
                },
                'presence-another': {
                    'user_count': 123
                }
            }
        }

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

    def trigger(self, event_name, data={}, socket_id=None, timeout=None):
        json_data = json.dumps(data, cls=self.pusher.encoder)
        path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, urllib.quote(self.name))
        url = self.pusher._get_url(path, 'POST', json_data, socket_id, name=event_name)
        status, resp_content = self.pusher.send_request(url,
                                                        'POST',
                                                        json_data,
                                                        timeout=timeout)
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

    def get_info(self, get_user_count=False, get_subscription_count=False):
        """TODO: implement this
        http://pusher.com/docs/rest_api
        """
        path = '/apps/%s/channels/%s' % (self.pusher.app_id, urllib.quote(self.name))
        info_properties = []
        if get_user_count:
            info_properties.append('user_count')
        if get_subscription_count:
            info_properties.append('subscription_count')
        info = ",".join(info_properties)
        url = self.pusher._get_url(path, 'GET', info=info)
        status, resp_content = self.pusher.send_request(url, 'GET')
        return json.loads(resp_content)

    def get_users(self):
        """
        http://pusher.com/docs/rest_api
        """
        path = '/apps/%s/channels/%s/users' % (self.pusher.app_id, urllib.quote(self.name))
        url = self.pusher._get_url(path, 'GET')
        status, resp_content = self.pusher.send_request(url, 'GET')
        return json.loads(resp_content)


# App Engine Channel, only if we can import the lib
try:
    from google.appengine.api import urlfetch

    class GoogleAppEngineChannel(Channel):
        def __init__(self, *args, **kwargs):
            super(GoogleAppEngineChannel, self, *args, **kwargs)

            # Patch pusher's send_request()
            def send_request(pusher, url, request_type, data_string):
                method = getattr(urlfetch, request_type)
                response = urlfetch.fetch(
                    url=url,
                    payload=data_string,
                    method=method,
                    headers={'Content-Type': 'application/json'}
                )
                return response.status_code, response.content
            self.pusher.send_request = send_request
except ImportError:
    pass


# App Engine NDB channel, outer try import/except as it uses decorator
try:
    from google.appengine.ext import ndb

    class GaeNdbChannel(GoogleAppEngineChannel):
        @ndb.tasklet
        def trigger_async(self, event_name, request_type, data=None, socket_id=None):
            """Async trigger that in turn calls send_request_async"""
            if data is None:
                data = {}
            json_data = json.dumps(data)
            url = self.pusher._get_url(json_data, request_type, socket_id, name=event_name)
            status = yield self.send_request_async(url, request_type, json_data)
            if status == 202:
                raise ndb.Return(True)
            elif status == 401:
                raise AuthenticationError
            elif status == 404:
                raise NotFoundError
            else:
                raise Exception("Unexpected return status %s" % status)

        @ndb.tasklet
        def send_request_async(self, url, request_type, data_string):
            """Send request and yield while waiting for future result"""
            ctx = ndb.get_context()
            secure = (self.pusher.protocol == 'https')
            result = yield ctx.urlfetch(
                url=url,
                payload=data_string,
                method=request_type,
                headers={'Content-Type': 'application/json'},
                validate_certificate=secure,
            )
            raise ndb.Return(result.status_code)
except ImportError:
    pass


class TornadoChannel(Channel):
    def trigger(self, event, data={}, socket_id=None, callback=None, timeout=None):
        # Patch pusher's send_request()
        def send_request(pusher, url, request_type, data_string, timeout=None):
            import tornado.httpclient
            request = tornado.httpclient.HTTPRequest(url,
                                                     method=request_type,
                                                     body=data_string,
                                                     request_timeout=timeout)
            client = tornado.httpclient.AsyncHTTPClient()
            client.fetch(request, callback=callback)
            # Returning 202 to avoid Channel errors. Actual error handling takes place in callback.
            return 202, ""
        self.pusher.send_request = send_request
        return super(TornadoChannel, self).trigger(event, data, socket_id, timeout=timeout)


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
        """Should return a list of dicts of the format:
        {
            'channel': 'presence-something-something', # The name of your channel
            'name': 'member-added', # The name of the event
            'user_id': '12345', # Whatever you assigned your user_id to be in your authenticate() call
        }
        """
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
