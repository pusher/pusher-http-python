import os
import sys
import time
import httplib
import hmac
import json
import hashlib
import urllib
import re
import socket

host    = 'api.pusherapp.com'
port    = 80
app_id  = None
key     = None
secret  = None

channel_name_re = re.compile('^[-a-zA-Z0-9_=@,.;]+$')
app_id_re       = re.compile('^[0-9]+$')

def url2options(url):
    assert url.startswith('http://'), "invalid URL"
    url = url[7:]
    key, url = url.split(':', 1)
    secret, url = url.split('@', 1)
    host, url = url.split('/', 1)
    url, app_id = url.split('/', 1)
    return {'key': key, 'secret': secret, 'host': host, 'app_id': app_id}

def pusher_from_url(url=None):
    url = url or os.environ['PUSHER_URL']
    return Pusher(**url2options(url))

class Pusher(object):
    def __init__(self, app_id=None, key=None, secret=None, host=None, port=None, encoder=None):
        _globals = globals()
        self.app_id = str(app_id or _globals['app_id'])
        if not app_id_re.match(self.app_id):
            raise NameError("Invalid app id")
        self.key = key or _globals['key']
        self.secret = secret or _globals['secret']
        self.host = host or _globals['host']
        self.port = port or _globals['port']
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
        if not channel_name_re.match(self.name):
            raise NameError("Invalid channel id: %s" % self.name)
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, urllib.quote(self.name))

    def trigger(self, event, data={}, socket_id=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        json_data = json.dumps(data, cls=self.pusher.encoder)
        query_string = self.signed_query(event, json_data, socket_id)
        signed_path = "%s?%s" % (self.path, query_string)
        status, resp_content = self.send_request(signed_path, json_data, timeout=timeout)
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

    def signed_query(self, event, json_data, socket_id):
        query_string = self.compose_querystring(event, json_data, socket_id)
        string_to_sign = "POST\n%s\n%s" % (self.path, query_string)
        signature = hmac.new(self.pusher.secret, string_to_sign, hashlib.sha256).hexdigest()
        return "%s&auth_signature=%s" % (query_string, signature)

    def compose_querystring(self, event, json_data, socket_id):
        hasher = hashlib.md5()
        hasher.update(json_data)
        hash_str = hasher.hexdigest()
        ret = "auth_key=%s&auth_timestamp=%s&auth_version=1.0&body_md5=%s&name=%s" % (self.pusher.key, int(time.time()), hash_str, event)
        if socket_id:
            ret += "&socket_id=" + unicode(socket_id)
        return ret

    def send_request(self, signed_path, data_string, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        http = httplib.HTTPConnection(self.pusher.host, self.pusher.port, timeout=timeout)
        http.request('POST', signed_path, data_string, {'Content-Type': 'application/json'})
        resp = http.getresponse()
        return resp.status, resp.read()

    def authenticate(self, socket_id, custom_data=None):
        if custom_data:
            custom_data = json.dumps(custom_data, cls=self.pusher.encoder)

        auth = self.authentication_string(socket_id, custom_data)
        r = {'auth': auth}

        if custom_data:
            r['channel_data'] = custom_data

        return r

    def authentication_string(self, socket_id, custom_string=None):
      if not socket_id:
          raise Exception("Invalid socket_id")

      string_to_sign = "%s:%s" % (socket_id, self.name)

      if custom_string:
        string_to_sign += ":%s" % custom_string

      signature = hmac.new(self.pusher.secret, string_to_sign, hashlib.sha256).hexdigest()

      return "%s:%s" % (self.pusher.key,signature)

    def get_absolute_path(self, signed_path):
        return 'http://%s%s' % (self.pusher.host, signed_path)

class GoogleAppEngineChannel(Channel):
    def send_request(self, signed_path, data_string):
        from google.appengine.api import urlfetch
        response = urlfetch.fetch(
            url=self.get_absolute_path(signed_path),
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
        def trigger_async(self, event, data={}, socket_id=None):
            """Async trigger that in turn calls send_request_async"""
            json_data = json.dumps(data)
            status = yield self.send_request_async(self.signed_query(event, json_data, socket_id), json_data)
            if status == 202:
                raise ndb.Return(True)
            elif status == 401:
                raise AuthenticationError
            elif status == 404:
                raise NotFoundError
            else:
                raise Exception("Unexpected return status %s" % status)

        @ndb.tasklet
        def send_request_async(self, query_string, data_string):
            """Send request and yield while waiting for future result"""
            ctx = ndb.get_context()
            secure = 's' if self.pusher.port == 443 else ''
            absolute_url = 'http%s://%s%s?%s' % (secure, self.pusher.host, self.path, query_string)
            result = yield ctx.urlfetch(
                url=absolute_url,
                payload=data_string,
                method='POST',
                headers={'Content-Type': 'application/json'},
                validate_certificate=bool(secure),
                )
            raise ndb.Return(result.status_code)
except ImportError:
    pass

class TornadoChannel(Channel):
    def trigger(self, event, data={}, socket_id=None, callback=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.callback = callback
        return super(TornadoChannel, self).trigger(event, data, socket_id, timeout=timeout)

    def send_request(self, signed_path, data_string, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        timeout = None if timeout == socket._GLOBAL_DEFAULT_TIMEOUT else timeout
        import tornado.httpclient
        absolute_url = self.get_absolute_path(signed_path)
        request = tornado.httpclient.HTTPRequest(absolute_url, method='POST', body=data_string, request_timeout=timeout)
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

class AuthenticationError(Exception):
    pass

class NotFoundError(Exception):
    pass

class AppDisabledOrMessageQuotaError(Exception):
    pass

class UnexpectedReturnStatusError(Exception):
    pass

channel_type = Channel
