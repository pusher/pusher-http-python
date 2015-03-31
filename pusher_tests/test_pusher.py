# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import os
import unittest

from pusher import Config, Pusher
from pusher.util import GET

try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestPusher(unittest.TestCase):
    def setUp(self):
        self.pusher = Pusher.from_url(u'http://key:secret@somehost/apps/4')
        
    def test_app_id_should_be_text(self):
        self.assertRaises(TypeError, lambda: Pusher(key=u'key', secret=u'secret', ssl=False))
        self.assertRaises(TypeError, lambda: Pusher(app_id=4, key=u'key', secret=u'secret'))
        self.assertRaises(TypeError, lambda: Pusher(app_id=b'4', key=u'key', secret=u'secret'))

    def test_key_should_be_text(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', secret=u'secret'))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=4, secret=u'secret'))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=b'key', secret=u'secret'))

    def test_secret_should_be_text(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=4))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=b'secret'))
        
    def test_initialize_from_env(self):
        with mock.patch.object(os, 'environ', new={'PUSHER_URL':'https://plah:bob@somehost/apps/42'}):
            pusher = Pusher.from_env()
            self.assertEqual(pusher.conf.ssl, True)
            self.assertEqual(pusher.conf.key, u'plah')
            self.assertEqual(pusher.conf.secret, u'bob')
            self.assertEqual(pusher.conf.host, u'somehost')
            self.assertEqual(pusher.conf.app_id, u'42')

        with mock.patch.object(os, 'environ', new={'PUSHER_DSN':'https://plah:bob@somehost/apps/42'}):
            pusher = Pusher.from_env('PUSHER_DSN')
            self.assertEqual(pusher.conf.ssl, True)
            self.assertEqual(pusher.conf.key, u'plah')
            self.assertEqual(pusher.conf.secret, u'bob')
            self.assertEqual(pusher.conf.host, u'somehost')
            self.assertEqual(pusher.conf.app_id, u'42')

    def test_trigger_success_case(self):
        json_dumped = u'{"message": "hello world"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:
            request = self.pusher.trigger.make_request([u'some_channel'], u'some_event', {u'message': u'hello world'})

            self.assertEqual(request.path, u'/apps/4/events')
            self.assertEqual(request.method, u'POST')

            expected_params = {
                u'channels': [u'some_channel'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)

        json_dumps_mock.assert_called_once({u'message': u'hello world'})

    def test_trigger_disallow_single_channel(self):
        self.assertRaises(TypeError, lambda:
            self.pusher.trigger.make_request(u'some_channel', u'some_event', {u'message': u'hello world'}))

    def test_trigger_disallow_invalid_channels(self):
        self.assertRaises(ValueError, lambda:
            self.pusher.trigger.make_request([u'some_channel!'], u'some_event', {u'message': u'hello world'}))

    def test_channels_info_default_success_case(self):
        request = self.pusher.channels_info.make_request()

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {})

    def test_channels_info_with_prefix_success_case(self):
        request = self.pusher.channels_info.make_request(prefix_filter='test')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {u'filter_by_prefix': u'test'})

    def test_channels_info_with_attrs_success_case(self):
        request = self.pusher.channels_info.make_request(attributes=[u'attr1', u'attr2'])

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {u'info': u'attr1,attr2'})

    def test_channel_info_success_case(self):
        request = self.pusher.channel_info.make_request(u'some_channel')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/some_channel')
        self.assertEqual(request.params, {})

    def test_channel_info_with_attrs_success_case(self):
        request = self.pusher.channel_info.make_request(u'some_channel', attributes=[u'attr1', u'attr2'])

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/some_channel')
        self.assertEqual(request.params, {u'info': u'attr1,attr2'})

    def test_user_info_success_case(self):
        request = self.pusher.users_info.make_request(u'presence-channel')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/presence-channel/users')
        self.assertEqual(request.params, {})

if __name__ == '__main__':
    unittest.main()
