app_id = None
key    = None
secret = None

class Pusher(object):
    def __init__(self, app_id=None, key=None, secret=None):
        _globals = globals()
        self.app_id = app_id or _globals['app_id']
        self.key = key or _globals['key']
        self.secret = secret or _globals['secret']