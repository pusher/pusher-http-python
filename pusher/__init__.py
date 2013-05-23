import httplib, time, sys, hmac

try:
    import json
    # some old versions of json lib don't implement dumps()
    if not hasattr(json, "dumps"):
        raise ImportError
except ImportError:
    import simplejson as json

# 2.4 hashlib implementation: http://code.krypto.org/python/hashlib/
import hashlib
import os
import urllib
import re
import socket

sha_constructor = hashlib.sha256

# But 2.4 hmac isn't compatible with hashlib.sha256 so use this wrapper
# http://www.schwarz.eu/opensource/projects/trac_captcha/browser/trac_captcha/cryptobox.py?rev=79%3Aed771e5252dc#L34
class AlgorithmWrapper(object):
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.digest_size = self.algorithm().digest_size

    def new(self, *args, **kwargs):
        return self.algorithm(*args, **kwargs)

if sys.version_info < (2, 5):
    sha_constructor = AlgorithmWrapper(hashlib.sha256)

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

class Channel(object):
    def __init__(self, name, pusher):
        self.pusher = pusher
        self.name = str(name)
        if not channel_name_re.match(self.name):
            raise NameError("Invalid channel id")
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, urllib.quote(self.name))

    def trigger(self, event, data={}, socket_id=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        json_data = json.dumps(data, cls=self.pusher.encoder)
        query_string = self.signed_query(event, json_data, socket_id)
        signed_path = "%s?%s" % (self.path, query_string)
        status = self.send_request(signed_path, json_data, timeout=timeout)
        if status == 202:
            return True
        elif status == 401:
            raise AuthenticationError
        elif status == 404:
            raise NotFoundError
        else:
            raise Exception("Unexpected return status %s" % status)

    def signed_query(self, event, json_data, socket_id):
        query_string = self.compose_querystring(event, json_data, socket_id)
        string_to_sign = "POST\n%s\n%s" % (self.path, query_string)
        signature = hmac.new(self.pusher.secret, string_to_sign, sha_constructor).hexdigest()
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
        return http.getresponse().status

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

      signature = hmac.new(self.pusher.secret, string_to_sign, sha_constructor).hexdigest()

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
        return response.status_code

class TornadoChannel(Channel):
    def trigger(self, event, data={}, socket_id=None, callback=None):
        self.callback = callback
        return super(TornadoChannel, self).trigger(event, data, socket_id)

    def send_request(self, signed_path, data_string):
        import tornado.httpclient
        absolute_url = self.get_absolute_path(signed_path)
        request = tornado.httpclient.HTTPRequest(absolute_url, method='POST', body=data_string)
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, callback=self.callback)
        return 202 # Returning 202 to avoid Channel errors. Actual error handling takes place in callback.

class AuthenticationError(Exception):
    pass

class NotFoundError(Exception):
    pass

channel_type = Channel
