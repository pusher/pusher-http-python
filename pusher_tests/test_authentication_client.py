# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import os
import six
import hmac
import json
import hashlib
import unittest
import time
from decimal import Decimal

from pusher.authentication_client import AuthenticationClient
from pusher.signature import sign, verify

try:
    import unittest.mock as mock
except ImportError:
    import mock


class TestAuthenticationClient(unittest.TestCase):
    def test_authenticate_for_private_channels(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        expected = {
            u'auth': u"foo:89955e77e1b40e33df6d515a5ecbba86a01dc816a5b720da18a06fd26f7d92ff"
        }

        self.assertEqual(authenticationClient.authenticate(u'private-channel', u'345.23'), expected)


    def test_authenticate_types(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        self.assertRaises(TypeError, lambda: authenticationClient.authenticate(2423, u'34554'))
        self.assertRaises(TypeError, lambda: authenticationClient.authenticate(u'plah', 234234))
        self.assertRaises(ValueError, lambda: authenticationClient.authenticate(u'::', u'345345'))


    def test_authenticate_for_presence_channels(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        custom_data = {
            u'user_id': u'fred',
            u'user_info': {
                u'key': u'value'
            }
        }

        expected = {
            u'auth': u"foo:e80ba6439492c2113022c39297a87a948de14061cc67b5788e045645a68b8ccd",
            u'channel_data': u"{\"user_id\":\"fred\",\"user_info\":{\"key\":\"value\"}}"
        }

        with mock.patch('json.dumps', return_value=expected[u'channel_data']) as dumps_mock:
            actual = authenticationClient.authenticate(u'presence-channel', u'345.43245', custom_data)

        self.assertEqual(actual, expected)
        dumps_mock.assert_called_once_with(custom_data, cls=None)


    def test_validate_webhook_success_case(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        body = u'{"time_ms": 1000000}'
        signature = six.text_type(hmac.new(authenticationClient.secret.encode('utf8'), body.encode('utf8'), hashlib.sha256).hexdigest())

        with mock.patch('time.time', return_value=1200):
            self.assertEqual(authenticationClient.validate_webhook(authenticationClient.key, signature, body), {u'time_ms': 1000000})


    def test_validate_webhook_bad_types(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        authenticationClient.validate_webhook(u'key', u'signature', u'body')

        # These things are meant to be human readable, so enforcing being
        # text is sensible.

        with mock.patch('time.time') as time_mock:
            self.assertRaises(TypeError, lambda: authenticationClient.validate_webhook(4, u'signature', u'body'))
            self.assertRaises(TypeError, lambda: authenticationClient.validate_webhook(u'key', 4, u'body'))
            self.assertRaises(TypeError, lambda: authenticationClient.validate_webhook(u'key', u'signature', 4))

        time_mock.assert_not_called()


    def test_validate_webhook_bad_key(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        body = u'some body'
        signature = six.text_type(hmac.new(authenticationClient.secret.encode(u'utf8'), body.encode(u'utf8'), hashlib.sha256).hexdigest())

        with mock.patch('time.time') as time_mock:
            self.assertEqual(authenticationClient.validate_webhook(u'badkey', signature, body), None)

        time_mock.assert_not_called()


    def test_validate_webhook_bad_signature(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        body = u'some body'
        signature = u'some signature'

        with mock.patch('time.time') as time_mock:
            self.assertEqual(authenticationClient.validate_webhook(authenticationClient.key, signature, body), None)

        time_mock.assert_not_called()


    def test_validate_webhook_bad_time(self):
        authenticationClient = AuthenticationClient(
            key=u'foo', secret=u'bar', host=u'host', app_id=u'4', ssl=True)

        body = u'{"time_ms": 1000000}'
        signature = six.text_type(hmac.new(authenticationClient.secret.encode('utf8'), body.encode('utf8'), hashlib.sha256).hexdigest())

        with mock.patch('time.time', return_value=1301):
            self.assertEqual(authenticationClient.validate_webhook(authenticationClient.key, signature, body), None)


if __name__ == '__main__':
    unittest.main()
