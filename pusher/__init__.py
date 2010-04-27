import httplib, md5, time, hashlib, hmac, base64

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
        self._channels[name] = Channel(name, self)
        return self._channels[name]

class Channel(object):
    def __init__(self, name, pusher):
        self.pusher = pusher
        self.name = name
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, self.name)

    def trigger(self, event, data={}):
        http = httplib.HTTPConnection(self.pusher.host, self.pusher.port)
        signed_path = '%s?%s' % (self.path, self.signed_query(event, data))
        http.request('POST', signed_path, data)
        return http.getresponse().read()

    def signed_query(self, event, data):
        query_string = self.compose_querystring(event, data)
        string_to_sign = "POST\n%s\n%s" % (self.path, query_string)
        binary_signature = hmac.new(self.pusher.secret, string_to_sign, hashlib.sha256).digest()
        signature = base64.b64encode(binary_signature).strip()
        return "%s&auth_signature=%s" % (query_string, signature)

    def compose_querystring(self, event, data):
        return "auth_key=%s&auth_timestamp=%s&auth_version=1.0&body_md5=%s&name=%s" % (self.pusher.key, int(time.time()), md5.new(json.dumps(data)).hexdigest(), event)
