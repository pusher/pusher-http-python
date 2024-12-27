# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import collections
import hashlib
import os
import re
import six
import time

from pusher.util import (
    ensure_text,
    pusher_url_re,
    doc_string, validate_user_id)

from pusher.pusher_client import PusherClient
from pusher.authentication_client import AuthenticationClient


class Pusher(object):
    """Client for the Pusher HTTP API.

    This client supports various backend adapters to support various http
    libraries available in the python ecosystem.

    :param app_id:  a pusher application identifier
    :param key:     a pusher application key
    :param secret:  a pusher application secret token
    :param ssl:     Whenever to use SSL or plain HTTP
    :param host:    Used for custom host destination
    :param port:    Used for custom port destination
    :param timeout: Request timeout (in seconds)
    :param encryption_master_key: deprecated, use encryption_master_key_base64
    :param encryption_master_key_base64: Used to derive a shared secret
      between server and the clients for payload encryption/decryption
    :param cluster: Convention for clusters other than the original Pusher cluster.
      Eg: 'eu' will resolve to the api-eu.pusherapp.com host
    :param backend: an http adapter class (AsyncIOBackend, RequestsBackend,
      SynchronousBackend, TornadoBackend)
    :param backend_options: additional backend
    """
    def __init__(
        self,
        app_id,
        key,
        secret,
        ssl=True,
        host=None,
        port=None,
        timeout=5,
        cluster=None,
        encryption_master_key=None,
        encryption_master_key_base64=None,
        json_encoder=None,
        json_decoder=None,
        backend=None,
        **backend_options):

        self._pusher_client = PusherClient(
            app_id,
            key,
            secret,
            ssl,
            host,
            port,
            timeout,
            cluster,
            encryption_master_key,
            encryption_master_key_base64,
            json_encoder,
            json_decoder,
            backend,
            **backend_options)

        self._authentication_client = AuthenticationClient(
            app_id,
            key,
            secret,
            ssl,
            host,
            port,
            timeout,
            cluster,
            encryption_master_key,
            encryption_master_key_base64,
            json_encoder,
            json_decoder,
            backend,
            **backend_options)

    @classmethod
    def from_url(cls, url, **options):
        """Alternative constructor that extracts the information from a URL.

        :param url: String containing a URL

        Usage::

          >> from pusher import Pusher
          >> p =
            Pusher.from_url("http://mykey:mysecret@api.pusher.com/apps/432")
        """
        m = pusher_url_re.match(ensure_text(url, "url"))
        if not m:
            raise Exception("Unparsable url: %s" % url)

        ssl = m.group(1) == 'https'

        options_ = {
            'key': m.group(2),
            'secret': m.group(3),
            'host': m.group(4),
            'app_id': m.group(5),
            'ssl': ssl}

        options_.update(options)

        return cls(**options_)

    @classmethod
    def from_env(cls, env='PUSHER_URL', **options):
        """Alternative constructor that extracts the information from an URL
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

        return cls.from_url(val, **options)

    @doc_string(PusherClient.trigger.__doc__)
    def trigger(self, channels, event_name, data, socket_id=None):
        return self._pusher_client.trigger(
            channels, event_name, data, socket_id)

    @doc_string(PusherClient.trigger.__doc__)
    def send_to_user(self, user_id, event_name, data):
        validate_user_id(user_id)
        user_server_string = "#server-to-user-%s" % user_id
        return self._pusher_client.trigger([user_server_string], event_name, data)

    @doc_string(PusherClient.trigger_batch.__doc__)
    def trigger_batch(self, batch=[], already_encoded=False):
        return self._pusher_client.trigger_batch(batch, already_encoded)

    @doc_string(PusherClient.channels_info.__doc__)
    def channels_info(self, prefix_filter=None, attributes=[]):
        return self._pusher_client.channels_info(prefix_filter, attributes)

    @doc_string(PusherClient.channel_info.__doc__)
    def channel_info(self, channel, attributes=[]):
        return self._pusher_client.channel_info(channel, attributes)

    @doc_string(PusherClient.users_info.__doc__)
    def users_info(self, channel):
        return self._pusher_client.users_info(channel)

    @doc_string(PusherClient.terminate_user_connections.__doc__)
    def terminate_user_connections(self, user_id):
        return self._pusher_client.terminate_user_connections(user_id)

    @doc_string(AuthenticationClient.authenticate.__doc__)
    def authenticate(self, channel, socket_id, custom_data=None):
        return self._authentication_client.authenticate(
            channel, socket_id, custom_data)

    @doc_string(AuthenticationClient.authenticate_user.__doc__)
    def authenticate_user(self, socket_id, user_data=None):
        return self._authentication_client.authenticate_user(
            socket_id, user_data
        )

    @doc_string(AuthenticationClient.validate_webhook.__doc__)
    def validate_webhook(self, key, signature, body):
        return self._authentication_client.validate_webhook(
            key, signature, body)
