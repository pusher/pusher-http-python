import httplib

host    = 'staging.api.pusherapp.com'
port    = 80
app_id  = None
key     = None
secret  = None

class Pusher(object):
    def __init__(self, app_id=None, key=None, secret=None):
        _globals = globals()
        self.app_id = app_id or _globals['app_id']
        self.key = key or _globals['key']
        self.secret = secret or _globals['secret']
        self.host = host or _globals['host']
        self.port = host or _globals['port']
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
        self.url = 'http://%s/app/%s/channel/%s' % (self.pusher.host, self.pusher.key, self.name)

    def trigger(self):
        http = httplib.HTTPConnection(self.pusher.host, self.pusher.port)
        http.request('POST', self.url)
        return http.getresponse().read()
