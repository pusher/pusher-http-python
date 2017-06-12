# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

from pusher.client import Client
from pusher.http import POST, PUT, DELETE, Request, request_method
from pusher.util import ensure_text


class NotificationClient(Client):

    DEFAULT_HOST = "nativepush-cluster1.pusher.com"
    API_PREFIX = 'server_api'
    API_VERSION = 'v1'

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
            self._host = self.DEFAULT_HOST

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
            (self.API_PREFIX, self.API_VERSION, self.app_id))

        return Request(self, POST, path, params)


class ClientNotificationClient(Client):

    DEFAULT_HOST = "nativepushclient-cluster1.pusher.com"
    API_PREFIX = 'client_api'
    API_VERSION = 'v1'
    APNS = 'apns'

    def __init__(
            self, app_id, key, secret, ssl=True, host=None, port=None,
            timeout=5, cluster=None, json_encoder=None, json_decoder=None,
            backend=None, client_id=None, **backend_options):
        super(ClientNotificationClient, self).__init__(
            app_id, key, secret, ssl, host, port, timeout, cluster,
            json_encoder, json_decoder, backend, **backend_options)

        self.client_id = client_id

        if host:
            self._host = ensure_text(host, "host")
        else:
            self._host = self.DEFAULT_HOST

    @request_method
    def register_request(self, device_token):
        """Register a device for push notifications, see:

        https://pusher.com/docs/push_notifications/reference/client_api
        """
        if not isinstance(device_token, basestring):
            raise TypeError("Device Token must be a string")

        if len(device_token) is 0:
            raise ValueError("Device Token must not be empty")

        path = '/{}/{}/clients'.format(self.API_PREFIX, self.API_VERSION)
        params = {
            'app_key': self.key,
            'platform_type': self.APNS,
            'token': device_token
        }
        return Request(self, POST, path, params)

    def register(self, device_token):
        """Wrapper to get response data, and store the returned client_id
        """
        data = self.register_request(device_token)
        self.client_id = data['id']
        return data

    @request_method
    def update_token(self, device_token):
        """Update a device for push notifications, see:

        https://pusher.com/docs/push_notifications/reference/client_api
        """
        if not self.client_id:
            raise ValueError(
                "Not registered! You must supply a client_id or register to receive one."
            )

        if not isinstance(device_token, basestring):
            raise TypeError("Device Token must be a string")

        if len(device_token) is 0:
            raise ValueError("Device Token must not be empty")

        path = '/{}/{}/clients/{}/token'.format(self.API_PREFIX, self.API_VERSION, self.client_id)
        params = {
            'app_key': self.key,
            'platform_type': self.APNS,
            'token': device_token
        }
        return Request(self, PUT, path, params)

    @request_method
    def subscribe(self, interest):
        """Subscribe a client to an interest, see:

        https://pusher.com/docs/push_notifications/reference/client_api
        """
        if not self.client_id:
            raise ValueError(
                "Not registered! You must supply a client_id or register to receive one."
            )

        if not isinstance(interest, basestring):
            raise TypeError("Interest must be a string")

        if len(interest) is 0:
            raise ValueError("Interest must not be empty")

        path = '/{}/{}/clients/{}/interests/{}'.format(
            self.API_PREFIX, self.API_VERSION, self.client_id, interest
        )
        params = {
            'app_key': self.key,
        }
        return Request(self, POST, path, params)

    @request_method
    def unsubscribe(self, interest):
        """Unsubscribe a client from an interest, see:

        https://pusher.com/docs/push_notifications/reference/client_api
        """
        if not self.client_id:
            raise ValueError(
                "Not registered! You must supply a client_id or register to receive one."
            )

        if not isinstance(interest, basestring):
            raise TypeError("Interest must be a string")

        if len(interest) is 0:
            raise ValueError("Interest must not be empty")

        path = '/{}/{}/clients/{}/interests/{}'.format(
            self.API_PREFIX, self.API_VERSION, self.client_id, interest
        )
        params = {
            'app_key': self.key,
        }
        return Request(self, DELETE, path, params)
