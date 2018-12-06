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
import random
import nacl

from pusher.pusher_client import PusherClient
from pusher.http import GET
from pusher.crypto import *

try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestPusherClient(unittest.TestCase):
    def setUp(self):
        self.pusher_client = PusherClient(app_id=u'4', key=u'key', secret=u'secret', host=u'somehost')

    def test_host_should_be_text(self):
        PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')

        self.assertRaises(TypeError, lambda: PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=4))

    def test_cluster_should_be_text(self):
        PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')

        self.assertRaises(TypeError, lambda: PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=4))

    def test_encryption_master_key_should_be_text(self):
        PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu', encryption_master_key="8tW5FQLniQ1sBQFwrw7t6TVEsJZd10yY")

        self.assertRaises(TypeError, lambda: PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=4, encryption_master_key=48762478647865374856347856888764 ))

    def test_host_behaviour(self):
        conf = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
        self.assertEqual(conf.host, u'api.pusherapp.com', u'default host should be correct')

        conf = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')
        self.assertEqual(conf.host, u'api-eu.pusher.com', u'host should be overriden by cluster setting')

        conf = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')
        self.assertEqual(conf.host, u'foo', u'host should be overriden by host setting')

        conf = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu', host=u'plah')
        self.assertEqual(conf.host, u'plah', u'host should be used in preference to cluster')

    def test_trigger_with_channels_list_success_case(self):
        json_dumped = u'{"message": "hello world"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:
            request = self.pusher_client.trigger.make_request([u'some_channel'], u'some_event', {u'message': u'hello world'})

            self.assertEqual(request.path, u'/apps/4/events')
            self.assertEqual(request.method, u'POST')

            expected_params = {
                u'channels': [u'some_channel'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)

        # FIXME: broken
        #json_dumps_mock.assert_called_once_with({u'message': u'hello world'})

    def test_trigger_with_channel_string_success_case(self):
        json_dumped = u'{"message": "hello worlds"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:

            request = self.pusher_client.trigger.make_request(u'some_channel', u'some_event', {u'message': u'hello worlds'})

            expected_params = {
                u'channels': [u'some_channel'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)

    def test_trigger_batch_success_case(self):
        json_dumped = u'{"message": "something"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:

            request = self.pusher_client.trigger_batch.make_request([{
                        u'channel': u'my-chan',
                        u'name': u'my-event',
                        u'data': {u'message': u'something'}
                    }])

            expected_params = {
                u'batch': [{
                    u'channel': u'my-chan',
                    u'name': u'my-event',
                    u'data': json_dumped
                }]
            }

            self.assertEqual(request.params, expected_params)

    def test_trigger_with_private_encrypted_channel_string_fail_case_no_encryption_master_key_specified(self):

        pc = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True)

        with self.assertRaises(TypeError):
            pc.trigger(u'private-encrypted-tst', u'some_event', {u'message': u'hello worlds'})


    def test_trigger_with_public_channel_with_encryption_master_key_specified_success(self):
        json_dumped = u'{"message": "something"}'

        pc = PusherClient(app_id=u'4', key=u'key', secret=u'secret', encryption_master_key=u'8tW5FQLniQ1sBQFwrw7t6TVEsJZd10yY', ssl=True)

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:

            request = pc.trigger.make_request(u'donuts', u'some_event', {u'message': u'hello worlds'})
            expected_params = {
                u'channels': [u'donuts'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)

    def test_trigger_with_private_encrypted_channel_success(self):
        encryp_master_key=u'8tW5FQLniQ1sBQFwrw7t6TVEsJZd10yY'
        chan = u'private-encrypted-tst'
        payload = {u'message': u'hello worlds'}

        pc = PusherClient(app_id=u'4', key=u'key', secret=u'secret', encryption_master_key=encryp_master_key, ssl=True)

        request = pc.trigger.make_request(chan, u'some_event', payload)

        shared_secret = generate_shared_secret(chan, encryp_master_key)

        box = nacl.secret.SecretBox(shared_secret)

        # encrypt the data payload with nacl
        nonce_b64 = json.loads(request.params["data"])["nonce"]
        nonce = base64.b64decode(nonce_b64)
        encrypted = box.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"), nonce)

        # obtain the ciphertext
        cipher_text = encrypted.ciphertext
        # encode cipertext to base64
        cipher_text_b64 = base64.b64encode(cipher_text)

        # format expected output
        json_dumped = json.dumps({ "nonce" : nonce_b64, "ciphertext": cipher_text_b64 }, ensure_ascii=False)

        expected_params = {
            u'channels': [u'private-encrypted-tst'],
            u'data': json_dumped,
            u'name': u'some_event'
        }
        self.assertEqual(request.params, expected_params)

    def test_trigger_with_channel_string_success_case(self):
        json_dumped = u'{"message": "hello worlds"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:

            request = self.pusher_client.trigger.make_request(u'some_channel', u'some_event', {u'message': u'hello worlds'})

            expected_params = {
                u'channels': [u'some_channel'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)
    def test_trigger_disallow_non_string_or_list_channels(self):
        self.assertRaises(TypeError, lambda:
            self.pusher_client.trigger.make_request({u'channels': u'test_channel'}, u'some_event', {u'message': u'hello world'}))

    def test_trigger_disallow_invalid_channels(self):
        self.assertRaises(ValueError, lambda:
            self.pusher_client.trigger.make_request([u'so/me_channel!'], u'some_event', {u'message': u'hello world'}))

    def test_channels_info_default_success_case(self):
        request = self.pusher_client.channels_info.make_request()

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {})

    def test_channels_info_with_prefix_success_case(self):
        request = self.pusher_client.channels_info.make_request(prefix_filter='test')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {u'filter_by_prefix': u'test'})

    def test_channels_info_with_attrs_success_case(self):
        request = self.pusher_client.channels_info.make_request(attributes=[u'attr1', u'attr2'])

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels')
        self.assertEqual(request.params, {u'info': u'attr1,attr2'})

    def test_channel_info_success_case(self):
        request = self.pusher_client.channel_info.make_request(u'some_channel')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/some_channel')
        self.assertEqual(request.params, {})

    def test_channel_info_with_attrs_success_case(self):
        request = self.pusher_client.channel_info.make_request(u'some_channel', attributes=[u'attr1', u'attr2'])

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/some_channel')
        self.assertEqual(request.params, {u'info': u'attr1,attr2'})

    def test_user_info_success_case(self):
        request = self.pusher_client.users_info.make_request(u'presence-channel')

        self.assertEqual(request.method, GET)
        self.assertEqual(request.path, u'/apps/4/channels/presence-channel/users')
        self.assertEqual(request.params, {})


if __name__ == '__main__':
    unittest.main()
