# -*- coding: utf-8 -*-

import unittest
from pusher.notification_client import NotificationClient, ClientNotificationClient


class TestNotificationClient(unittest.TestCase):
    def setUp(self):
        self.client = NotificationClient(app_id='4', key='key', secret='secret')
        self.success_fixture = {
            'webhook_url': 'http://webhook.com',
            'webhook_level': 'DEBUG',
            'apns': {
                'alert': {
                    'title': 'yolo',
                    'body': 'woot'
                }
            },
            'gcm': {
                'notification': {
                    'title': 'yipee',
                    'icon': 'huh'
                }
            }
        }

    def test_host_should_be_text(self):
        NotificationClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')

        self.assertRaises(
            TypeError,
            lambda: NotificationClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=4)
        )

    def test_notify_success_case(self):
        request = self.client.notify.make_request(['yolo'], self.success_fixture)
        self.assertEqual(request.method, u'POST')
        self.assertEqual(request.base_url, u'https://nativepush-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/server_api/v1/apps/4/notifications')
        self.assertEqual(request.params, {
            'interests': ['yolo'],
            'webhook_url': 'http://webhook.com',
            'webhook_level': 'DEBUG',
            'apns': {
                'alert': {
                    'title': 'yolo',
                    'body': 'woot'
                }
            },
            'gcm': {
                'notification': {
                    'title': 'yipee',
                    'icon': 'huh'
                }
            }
        })

    def test_notify_supplied_ssl_and_host(self):
        configured_client = NotificationClient(
            app_id='6', key='woo', secret='shhh', ssl=False, host='foo.bar.io'
        )
        request = configured_client.notify.make_request([u'blargh'], self.success_fixture)
        self.assertEqual(request.base_url, u'http://foo.bar.io:80')

    def test_at_least_one_interest_sent_to(self):
        self.assertRaises(ValueError, lambda: self.client.notify([], self.success_fixture))


class TestClientNotificationClient(unittest.TestCase):

    def setUp(self):
        self.client = ClientNotificationClient(
            app_id='4', key='key', secret='secret', client_id='123'
        )

    def test_register_request(self):
        client = ClientNotificationClient(app_id='4', key='key', secret='secret')
        request = client.register_request.make_request('device_token')
        self.assertEqual(request.method, u'POST')
        self.assertEqual(request.base_url, u'https://nativepushclient-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/client_api/v1/clients')
        self.assertEqual(request.params, {
            'app_key': 'key',
            'platform_type': 'apns',
            'token': 'device_token',
        })

    def test_update_token(self):
        request = self.client.update_token.make_request('device_token')
        self.assertEqual(request.method, u'PUT')
        self.assertEqual(request.base_url, u'https://nativepushclient-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/client_api/v1/clients/123/token')
        self.assertEqual(request.params, {
            'app_key': 'key',
            'platform_type': 'apns',
            'token': 'device_token',
        })

    def test_subscribe(self):
        request = self.client.subscribe.make_request('interest')
        self.assertEqual(request.method, u'POST')
        self.assertEqual(request.base_url, u'https://nativepushclient-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/client_api/v1/clients/123/interests/interest')
        self.assertEqual(request.params, {
            'app_key': 'key',
        })

    def test_unsubscribe(self):
        request = self.client.unsubscribe.make_request('interest')
        self.assertEqual(request.method, u'DELETE')
        self.assertEqual(request.base_url, u'https://nativepushclient-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/client_api/v1/clients/123/interests/interest')
        self.assertEqual(request.params, {
            'app_key': 'key',
        })


if __name__ == '__main__':
    unittest.main()
