# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

from pusher.client import Client
from pusher.http import POST, Request, request_method
from pusher.util import ensure_text


DEFAULT_HOST = "nativepush-cluster1.pusher.com"
RESTRICTED_GCM_KEYS = ['to', 'registration_ids']
API_PREFIX = 'server_api'
API_VERSION = 'v1'
GCM_TTL = 241920
WEBHOOK_LEVELS = ['INFO', 'DEBUG', '']


class NotificationClient(Client):
    def __init__(
            self, app_id, key, secret, ssl=True, host=None, port=None,
            timeout=5, cluster=None, json_encoder=None, json_decoder=None,
            backend=None, **backend_options):
        super(NotificationClient, self).__init__(
            app_id, key, secret, ssl, host, port, timeout, cluster,
            json_encoder, json_decoder, backend, **backend_options)

        if host:
            self._host = ensure_text(host, "host")

        else:
            self._host = DEFAULT_HOST


    @request_method
    def notify(self, interests, notification):
        """Send push notifications, see:

        https://github.com/pusher/pusher-http-python#push-notifications-beta
        """
        if not isinstance(interests, list) and not isinstance(interests, set):
            raise TypeError("Interests must be a list or a set")

        if len(interests) is 0:
            raise ValueError("Interests must not be empty")

        if not isinstance(notification, dict):
            raise TypeError("Notification must be a dictionary")

        params = {
            'interests': interests}

        params.update(notification)
        path = (
            "/%s/%s/apps/%s/notifications" %
            (API_PREFIX, API_VERSION, self.app_id))

        return Request(self, POST, path, params)
