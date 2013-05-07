# 2.4 hashlib implementation: http://code.krypto.org/python/hashlib/
import hashlib
import hmac
import httplib
import os
import string
import sys
import time

try:
    import json
    # some old versions of json lib don't implement dumps()
    if not hasattr(json, "dumps"):
        raise ImportError
except ImportError:
    import simplejson as json

sha_constructor = hashlib.sha256

# http://pusher.com/docs/client_api_guide/client_channels#naming-channels
CHANNEL_ALLOWED_CHARS = string.ascii_letters + string.digits + '_-=@,.;'
EVENT_ALLOWED_CHARS = string.ascii_letters + string.digits + '_-'
TRANS_TABLE = string.maketrans('', '')


def verify_chars(chars, allowed_chars):
    """Verify chars against allowed_chars, using translate (which is fast)"""
    invalid_chars = str(chars).translate(TRANS_TABLE, allowed_chars)
    if invalid_chars:
        raise ValueError('Invalid chars: %s' % invalid_chars)
    return True


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


def url2options(url):
    """Extract options from url"""
    if not url.startswith('http://'):
        raise ValueError("invalid URL")
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
    """
    Pusher representation, holds config and channels

    Attributes:
        app_id: App id as registered with pusher
        key: App key
        secret: App secret
        host: Pusher host, default api.pusherapp.com
        port: Pusher server port, by default 80
        channel_factory: Factory for creating channel, uses Channel class if None
        json_dumps: JSON dumps function for serializing data
        keep_channels: Whether to keep channels around for reuse, default True
    """
    def __init__(self, app_id=None, key=None, secret=None, host='api.pusherapp.com', port=80,
                 channel_factory=None, json_dumps=json.dumps, keep_channels=True):
        self.app_id = app_id
        self.key = key
        self.secret = secret
        self.host = host
        self.port = port
        self.channel_factory = channel_factory or Channel
        self.json_dumps = json_dumps
        self.keep_channels = keep_channels
        self._channels = {}

    def __getitem__(self, key):
        if not key in self._channels:
            return self._make_channel(key)
        return self._channels[key]

    def _make_channel(self, name):
        self.verify_channel_name(name)
        channel = self.channel_factory(name, self)
        if self.keep_channels:
            self._channels[name] = channel
        return channel

    @staticmethod
    def verify_channel_name(name):
        """Verify channel name against CHANNEL_ALLOWED_CHARS, using translate"""
        return verify_chars(name, CHANNEL_ALLOWED_CHARS)


class Channel(object):
    """
    Channel responsible for sending the request to pusher server

    Attributes:
        pusher: Pusher instance
        name: Channel name
        path: REST path on pusher server, including app id and channel name
    """
    def __init__(self, name, pusher):
        self.pusher = pusher
        self.name = name
        self.path = '/apps/%s/channels/%s/events' % (self.pusher.app_id, self.name)

    @staticmethod
    def verify_event_name(name):
        """Verify channel name against CHANNEL_ALLOWED_CHARS, using translate"""
        return verify_chars(name, EVENT_ALLOWED_CHARS)

    def trigger(self, event, data={}, socket_id=None):
        """
        Send event to pusher server

        Arguments:
            event: Event name sent to client
            data: Optional additional data to be sent to client, serialized as JSON
            socket_id: Optional socket id to specify sockets for channel
        Returns:
            result of decide_outcome, True or exception
        """
        self.verify_event_name(event)
        json_data = self.pusher.json_dumps(data)
        status = self.send_request(self.signed_query(event, json_data, socket_id), json_data)
        return self.decide_outcome(status)

    @staticmethod
    def decide_outcome(status):
        """
        Decide outcome based on http status code from pusher server

        This is separate method as it's used by extended Channels

        Arguments:
            status: HTTP status code
        Returns:
            True if request was accepted (2xx)
        Raises:
            AuthenticationError if not authenticated
            NotFoundError if channel name was not NotFoundError
            Exception on other errors or responses from  server
        """
        if status // 100 == 2:
            return True
        elif status == 400:
            raise BadRequestError
        elif status == 401:
            raise AuthenticationError
        elif status == 403:
            raise ForbiddenError
        elif status == 404:
            raise NotFoundError
        elif status == 413:
            raise TooLargeError
        else:
            raise PusherError("Unexpected return status %s" % status)

    def signed_query(self, event, json_data, socket_id):
        """
        Make signed query string
        Arguments:
            event: Event name sent to client
            data: Optional additional data to be sent to client, serialized as JSON
            socket_id: Optional socket id to specify sockets for channel
        Returns:
            query string including auth_signature
        """
        query_string = self.compose_querystring(event, json_data, socket_id)
        string_to_sign = "POST\n%s\n%s" % (self.path, query_string)
        signature = hmac.new(self.pusher.secret, string_to_sign, sha_constructor).hexdigest()
        return "%s&auth_signature=%s" % (query_string, signature)

    def compose_querystring(self, event, json_data, socket_id):
        """
        Assemble query string and include hash string
        """
        hasher = hashlib.md5()
        hasher.update(json_data)
        hash_str = hasher.hexdigest()
        ret = "auth_key=%s&auth_timestamp=%s&auth_version=1.0&body_md5=%s&name=%s" % (
            self.pusher.key, int(time.time()), hash_str, event)
        if socket_id:
            ret += "&socket_id=" + unicode(socket_id)
        return ret

    def send_request(self, query_string, data_string):
        """
        Send request to pusher server, check status

        Arguments:
            query_string: Query string included in URL
            data_string: HTTP body as JSON
        Returns:
            Tuple of HTTP status code and body
        """
        signed_path = '%s?%s' % (self.path, query_string)
        http = httplib.HTTPConnection(self.pusher.host, self.pusher.port)
        http.request('POST', signed_path, data_string, {'Content-Type': 'application/json'})
        return http.getresponse().status

    def authenticate(self, socket_id, custom_data=None):
        if custom_data:
            custom_data = self.pusher.json_dumps(custom_data)

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

        return "%s:%s" % (self.pusher.key, signature)


class PusherError(Exception):
    """General error class for pusher responses"""


class AuthenticationError(PusherError):
    """Authentication error: response body will contain an explanation"""


class NotFoundError(PusherError):
    """Resource not found"""


class BadRequestError(PusherError):
    """Error: details in response body"""


class ForbiddenError(PusherError):
    """Forbidden: app disabled or over message quota"""


class TooLargeError(PusherError):
    """Data parameter is limited to 10k"""
