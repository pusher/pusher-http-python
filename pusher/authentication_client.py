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
import base64

from pusher.util import (
    ensure_text,
    ensure_binary,
    validate_channel,
    validate_socket_id,
    channel_name_re
    )

from pusher.client import Client
from pusher.http import GET, POST, Request, request_method
from pusher.signature import sign, verify
from pusher.crypto import *


class AuthenticationClient(Client):
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

        super(AuthenticationClient, self).__init__(
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
        response_payload = { "auth": auth }

        if is_encrypted_channel(channel):
            shared_secret = generate_shared_secret(
                ensure_binary(channel, "channel"), self._encryption_master_key)
            shared_secret_b64 = base64.b64encode(shared_secret)
            response_payload["shared_secret"] = shared_secret_b64

        if custom_data:
            response_payload['channel_data'] = custom_data

        return response_payload


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
