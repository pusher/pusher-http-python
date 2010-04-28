import httplib, time, hashlib, hmac, base64

try:
    import json
except ImportError:
    import simplejson as json

host    = 'api.pusherapp.com'
port    = 80
app_id  = None
key     = None
secret  = None

class Pusher(object):
    def __init__(self, app_id=None, key=None, secret=None, host=None, port=None):
        _globals = globals()
        self.app_id = app_id or _globals['app_id']
        self.key = key or _globals['key']
        self.secret = secret or _globals['secret']
        self.host = host or _globals['host']
        self.port = port or _globals['port']
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
        self.name = name
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, self.name)

    def trigger(self, event, data={}, socket_id=None):
        json_data = json.dumps(data)
        status = self.send_request(self.signed_query(event, json_data, socket_id), json_data)
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

    def send_request(self, query_string, data_string):
        signed_path = '%s?%s' % (self.path, query_string)
        http = httplib.HTTPConnection(self.pusher.host, self.pusher.port)
        http.request('POST', signed_path, data_string)
        return http.getresponse().status

class GoogleAppEngineChannel(Channel):
    def send_request(self, query_string, data_string):
        from google.appengine.api import urlfetch
        absolute_url = 'http://%s/%s?%s' % (self.pusher.host, self.path, query_string)
        response = urlfetch.fetch(
            url=absolute_url,
            payload=data_string,
            method=urlfetch.POST,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code

class AuthenticationError(Exception):
    pass

class NotFoundError(Exception):
    pass

channel_type = Channel
