# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.config import Config
from pusher.request import Request
from pusher.sync import SynchronousBackend
from pusher.util import GET, POST, text, validate_channel, app_id_re, channel_name_re

import os
import collections
import json
import six
import hmac
import hashlib
import time

try:
    compare_digest = hmac.compare_digest
except AttributeError:
    # Not secure when the length is supposed to be kept secret
    def compare_digest(a, b):
        if len(a) != len(b):
            return False
        return reduce(lambda x, y: x | y, [ord(x) ^ ord(y) for x, y in zip(a, b)]) == 0

class RequestMethod(object):
    def __init__(self, pusher, f):
        self.pusher = pusher
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.pusher.backend.send_request(self.make_request(*args, **kwargs))

    def make_request(self, *args, **kwargs):
        return self.f(self.pusher, *args, **kwargs)

def doc_string(doc):
    def decorator(f):
        f.__doc__ = doc
        return f
    return decorator

def request_method(f):
    @property
    @doc_string(f.__doc__)
    def wrapped(self):
        return RequestMethod(self, f)
    return wrapped

def join_attributes(attributes):
    for attr in attributes:
        if not isinstance(attr, six.text_type):
            raise TypeError('Each attr should be %s' % text)

    return six.text_type(',').join(attributes)

class Pusher(object):
    """Client for the Pusher HTTP API.

    This client supports various backend adapters to support various http
    libraries available in the python ecosystem. 

    :param app_id: a pusher application identifier
    :param key:    a pusher application key
    :param secret: a pusher application secret token
    :param config: a pusher.Config instance
    :param backend: an object that responds to the send_request(request)
                    method. If none is provided, a
                    python.sync.SynchronousBackend instance is created.
    """
    def __init__(self, app_id, key, secret, config=None, backend=None):
        
        if not isinstance(app_id, six.text_type):
            raise TypeError("App ID should be %s" % text)
        if not app_id_re.match(app_id):
            raise ValueError("Invalid app id")

        if not isinstance(key, six.text_type):
            raise TypeError("Key should be %s" % text)

        if not isinstance(secret, six.text_type):
            raise TypeError("Secret should be %s" % text)
        
        if not config:
            config=Config(app_id=app_id, key=key, secret=secret)
        else:
            config.app_id=app_id
            config.key=key
            config.secret=secret
            
        if not isinstance(config, Config):
            raise TypeError("config should be a pusher.Config object")
            
        self.backend = backend or SynchronousBackend(config)
        self.config = config
        
    @classmethod
    def from_url(cls, url):
        """Alternate constructor that extracts the information from a URL.

        :param url: String containing a URL

        Usage::

          >> from pusher import Pusher
          >> p = Pusher.from_url("http://mykey:mysecret@api.pusher.com/apps/432")
        """
        config=Config.from_url(url)
        
        return cls(config.app_id, config.key, config.secret, config)
        
    @classmethod
    def from_env(cls, env='PUSHER_URL'):
        """Alternate constructor that extracts the information from an URL
        stored in an environment variable. The pusher heroku addon will set
        the PUSHER_URL automatically when installed for example.

        :param env: Name of the environment variable

        Usage::

          >> from pusher import Pusher
          >> c = Pusher.from_env("PUSHER_URL")
        """
        val = os.environ.get(env)
        if not val:
            raise Exception("Environment variable %s not found" % env)
        
        config=Config.from_url(six.text_type(val))
        return cls(config.app_id, config.key, config.secret, config)

    @request_method
    def trigger(self, channels, event_name, data, socket_id=None):
        '''
        Trigger an event on one or more channels, see:

        http://pusher.com/docs/rest_api#method-post-event
        '''
        
        if isinstance(channels, dict) or not (isinstance(channels, six.string_types) or isinstance(channels, (collections.Sized, collections.Iterable))):
            raise TypeError("Expected a single string or collection of channels (each channel should be %s)" % text)

        if isinstance(channels, six.string_types):
            channels = [channels]

        if len(channels) > 10:
            raise ValueError("Too many channels")

        for channel in channels:
            validate_channel(channel)

        if not isinstance(event_name, six.text_type):
            raise TypeError("event_name should be %s" % text)

        if len(event_name) > 200:
            raise ValueError("event_name too long")

        if not isinstance(data, six.text_type):
            data = json.dumps(data)

        if len(data) > 10240:
            raise ValueError("Too much data")

        params = {
            'name': event_name,
            'channels': channels,
            'data': data
        }
        if socket_id:
            if not isinstance(socket_id, six.text_type):
                raise TypeError("Socket ID should be %s" % text)
            params['socket_id'] = socket_id
        return Request(self.config, POST, "/apps/%s/events" % self.config.app_id, params)
        
    def authenticate(self, channel, socket_id, custom_data=None):
        """Used to generate delegated client subscription token.

        :param channel: name of the channel to authorize subscription to
        :param socket_id: id of the socket that requires authorization
        :param custom_data: used on presence channels to provide user info
        """
        if not isinstance(channel, six.text_type):
            raise TypeError('Channel should be %s' % text)

        if not channel_name_re.match(channel):
            raise ValueError('Channel should be a valid channel, got: %s' % channel)

        if not isinstance(socket_id, six.text_type):
            raise TypeError('Socket ID should %s' % text)

        if custom_data:
            custom_data = json.dumps(custom_data)

        string_to_sign = "%s:%s" % (socket_id, channel)

        if custom_data:
            string_to_sign += ":%s" % custom_data

        signature = hmac.new(self.config.secret.encode('utf8'), string_to_sign.encode('utf8'), hashlib.sha256).hexdigest()

        auth = "%s:%s" % (self.config.key, signature)
        result = {'auth': auth}

        if custom_data:
            result['channel_data'] = custom_data

        return result
        
    def validate_webhook(self, key, signature, body):
        """Used to validate incoming webhook messages. When used it guarantees
        that the sender is Pusher and not someone else impersonating it.

        :param key: key used to sign the body
        :param signature: signature that was given with the body
        :param body: content that needs to be verified
        """
        if not isinstance(key, six.text_type):
            raise TypeError('key should be %s' % text)

        if not isinstance(signature, six.text_type):
            raise TypeError('signature should be %s' % text)

        if not isinstance(body, six.text_type):
            raise TypeError('body should be %s' % text)

        if key != self.config.key:
            return None

        generated_signature = six.text_type(hmac.new(self.config.secret.encode('utf8'), body.encode('utf8'), hashlib.sha256).hexdigest())

        if not compare_digest(generated_signature, signature):
            return None

        try:
            body_data = json.loads(body)
        except ValueError:
            return None

        time_ms = body_data.get('time_ms')
        if not time_ms:
            return None

        print(abs(time.time()*1000 - time_ms))
        if abs(time.time()*1000 - time_ms) > 300000:
            return None

        return body_data

    @request_method
    def channels_info(self, prefix_filter=None, attributes=[]):
        '''
        Get information on multiple channels, see:

        http://pusher.com/docs/rest_api#method-get-channels
        '''
        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)
        if prefix_filter:
            params['filter_by_prefix'] = prefix_filter
        return Request(self.config, GET, "/apps/%s/channels" % self.config.app_id, params)

    @request_method
    def channel_info(self, channel, attributes=[]):
        '''
        Get information on a specific channel, see:

        http://pusher.com/docs/rest_api#method-get-channel
        '''
        validate_channel(channel)

        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)
        return Request(self.config, GET, "/apps/%s/channels/%s" % (self.config.app_id, channel), params)

    @request_method
    def users_info(self, channel):
        '''
        Fetch user ids currently subscribed to a presence channel

        http://pusher.com/docs/rest_api#method-get-users
        '''
        validate_channel(channel)

        return Request(self.config, GET, "/apps/%s/channels/%s/users" % (self.config.app_id, channel))
