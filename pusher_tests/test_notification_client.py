# -*- coding: utf-8 -*-

import unittest
from pusher.notification_client import NotificationClient

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

	def test_notify_success_case(self):
		request = self.client.notify.make_request(['yolo'], self.success_fixture)
		self.assertEqual(request.method, u'POST')
		self.assertEqual(request.base_url, u'https://yolo.ngrok.io:443')
		self.assertEqual(request.path, '/customer_api/v1/apps/4/notifications')
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
		configured_client = NotificationClient(app_id='6', key='woo', secret='shhh', ssl=False, host='foo.bar.io')
		request = configured_client.notify.make_request([u'blargh'], self.success_fixture)
		self.assertEqual(request.base_url, u'http://foo.bar.io:80')

	def test_either_apns_or_gcm_must_be_present(self):
		self.assertRaises(ValueError, lambda:
			self.client.notify([u'yolo'], {})
		)

	def test_only_one_interest_sent_to(self):
		self.assertRaises(ValueError, lambda: self.client.notify([u'yolo', u'woot'], self.success_fixture))

	def test_gcm_restricted_keys_removed(self):
		request = self.client.notify.make_request(['yolo'], {
			'gcm': {
				'to': 'woot',
				'registration_ids': ['woot', 'bla'],
				'notification': {
					'title': 'yipee',
					'icon': 'huh'
				}
			}
		})
		self.assertEqual(request.params, {
			'interests': ['yolo'],
			'gcm': {
				'notification': {
					'title': 'yipee',
					'icon': 'huh'
				}
			}
		})

	def test_gcm_validations(self):
		invalid_gcm_payloads = [
			{
				'gcm': {
					'time_to_live': -1,
					'notification': {
						'title': 'yipee',
						'icon': 'huh'
					}
				}
			},
			{
				'gcm': {
					'time_to_live': 241921,
					'notification': {
						'title': 'yipee',
						'icon': 'huh'
					}
				}
			},
			{
				'gcm': {
					'notification': {
						'title': 'yipee',
					}
				}
			},
			{
				'gcm': {
					'notification': {
						'icon': 'huh'
					}
				}
			},
			{
				'gcm': {
					'notification': {
						'title': '',
						'icon': 'huh'
					}
				}
			},
			{
				'gcm': {
					'notification': {
						'title': 'yipee',
						'icon': ''
					}
				}
			}
		]

		for payload in invalid_gcm_payloads:
			self.assertRaises(ValueError, lambda:
				self.client.notify([u'yolo'], payload)
			)

		valid_gcm_payload = \
			{
				'gcm': {
					'time_to_live': 42,
					'notification': {
						'title': 'yipee',
						'icon': 'huh'
					}
				}
			}
		self.client.notify.make_request([u'yolo'], valid_gcm_payload)

	def test_webhook_level_validation(self):
		invalid_webhook_configs = [
			{
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
			},
			{
				'webhook_level': 'FOOBAR',
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
			}]

		for config in invalid_webhook_configs:
			self.assertRaises(ValueError, lambda: self.client.notify.make_request([u'yolo'], config))
