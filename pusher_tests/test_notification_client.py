# -*- coding: utf-8 -*-

import unittest
from pusher.notification_client import NotificationClient

class TestNotificationClient(unittest.TestCase):
    def setUp(self):
        self.client = NotificationClient(app_id='4', key='key', secret='secret')
        self.success_fixture = {
            'webhook_url': 'http://webhook.com',
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

        self.assertRaises(TypeError, lambda: NotificationClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=4))

    def test_notify_success_case(self):
        request = self.client.notify.make_request(['yolo'], self.success_fixture)
        self.assertEqual(request.method, u'POST')
        self.assertEqual(request.base_url, u'https://nativepush-cluster1.pusher.com:443')
        self.assertEqual(request.path, '/server_api/v1/apps/4/notifications')
        self.assertEqual(request.params, {
            'interests': ['yolo'],
            'webhook_url': 'http://webhook.com',
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
        configured_client = NotificationClient(app_id='6', key='woo', secret='shhh', ssl=False, host='foo.bar.io')
        request = configured_client.notify.make_request([u'blargh'], self.success_fixture)
        self.assertEqual(request.base_url, u'http://foo.bar.io:80')

    def test_at_least_one_interest_sent_to(self):
        self.assertRaises(ValueError, lambda: self.client.notify([], self.success_fixture))


if __name__ == '__main__':
    unittest.main()
