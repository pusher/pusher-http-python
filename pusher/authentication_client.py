# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import collections
import hashlib
import json
import os
import re
import six
import time

from pusher.util import (
    ensure_text,
    validate_channel,
    validate_socket_id,
    channel_name_re)

from pusher.client import Client
from pusher.http import GET, POST, Request, request_method
from pusher.signature import sign, verify


class AuthenticationClient(Client):
    def __init__(
            self, app_id, key, secret, ssl=True, host=None, port=None,
            timeout=5, cluster=None, json_encoder=None, json_decoder=None,
            backend=None, **backend_options):
        super(AuthenticationClient, self).__init__(
            app_id, key, secret, ssl, host, port, timeout, cluster,
            json_encoder, json_decoder, backend, **backend_options)

        if host:
            self._host = ensure_text(host, "host")

        elif cluster:
            self._host = (
                six.text_type("api-%s.pusher.com") %
                ensure_text(cluster, "cluster"))
        else:
            self._host = six.text_type("api.pusherapp.com")


    def authenticate(self, channel, socket_id, custom_data=None):
        """Used to generate delegated client subscription token.

        :param channel: name of the channel to authorize subscription to
        :param socket_id: id of the socket that requires authorization
        :param custom_data: used on presence channels to provide user info
        """
        channel = validate_channel(channel)

        if not channel_name_re.match(channel):
            raise ValueError('Channel should be a valid channel, got: %s' % channel)

        socket_id = validate_socket_id(socket_id)

        if custom_data:
            custom_data = json.dumps(custom_data, cls=self._json_encoder)

        string_to_sign = "%s:%s" % (socket_id, channel)

        if custom_data:
            string_to_sign += ":%s" % custom_data

        signature = sign(self.secret, string_to_sign)

        auth = "%s:%s" % (self.key, signature)
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
        key = ensure_text(key, "key")
        signature = ensure_text(signature, "signature")
        body = ensure_text(body, "body")

        if key != self.key:
            return None

        if not verify(self.secret, body, signature):
            return None

        try:
            body_data = json.loads(body, cls=self._json_decoder)

        except ValueError:
            return None

        time_ms = body_data.get('time_ms')
        if not time_ms:
            return None

        if abs(time.time()*1000 - time_ms) > 300000:
            return None

        return body_data
