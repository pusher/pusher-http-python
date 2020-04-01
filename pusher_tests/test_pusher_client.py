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
import base64

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

    def test_trigger_batch_success_case_2(self):
        json_dumped = u'{"message": "something"}'

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:
            request = self.pusher_client.trigger_batch.make_request(
                    [{
                        u'channel': u'my-chan',
                        u'name': u'my-event',
                        u'data': {u'message': u'something'}
                    },{
                        u'channel': u'my-chan-2',
                        u'name': u'my-event-2',
                        u'data': {u'message': u'something-else'}
                    }])

            expected_params = {
                u'batch': [{
                    u'channel': u'my-chan',
                    u'name': u'my-event',
                    u'data': json_dumped
                },
                {
                    u'channel': u'my-chan-2',
                    u'name': u'my-event-2',
                    u'data': json_dumped
                }]
            }

            self.assertEqual(request.params, expected_params)

    def test_trigger_batch_with_mixed_channels_success_case(self):
        json_dumped = u'{"message": "something"}'

        master_key = b'8tW5FQLniQ1sBQFwrw7t6TVEsJZd10yY'
        master_key_base64 = base64.b64encode(master_key)
        event_name_2 = "my-event-2"
        chan_2 = "private-encrypted-2"
        payload = {"message": "hello worlds"}

        pc = PusherClient(
                app_id=u'4',
                key=u'key',
                secret=u'secret',
                encryption_master_key_base64=master_key_base64,
                ssl=True)
        request = pc.trigger_batch.make_request(
                [{
                    u'channel': u'my-chan',
                    u'name': u'my-event',
                    u'data': {u'message': u'something'}
                },{
                    u'channel': chan_2,
                    u'name': event_name_2,
                    u'data': payload
                }]
        )

        # simulate the same encryption process and check equality
        chan_2 = ensure_binary(chan_2, "chan_2")
        shared_secret = generate_shared_secret(chan_2, master_key)

        box = nacl.secret.SecretBox(shared_secret)

        nonce_b64 = json.loads(request.params["batch"][1]["data"])["nonce"].encode("utf-8")
        nonce = base64.b64decode(nonce_b64)

        encrypted = box.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf'-8"), nonce)

        # obtain the ciphertext
        cipher_text = encrypted.ciphertext

        # encode cipertext to base64
        cipher_text_b64 = base64.b64encode(cipher_text)

        # format expected output
        json_dumped_2 = json.dumps({ "nonce" : nonce_b64.decode("utf-8"), "ciphertext": cipher_text_b64.decode("utf-8") }, ensure_ascii=False)

        expected_params = {
            u'batch': [{
                u'channel': u'my-chan',
                u'name': u'my-event',
                u'data': json_dumped
            },
            {
                u'channel': u'private-encrypted-2',
                u'name': event_name_2,
                u'data': json_dumped_2
            }]
        }

        self.assertEqual(request.params, expected_params)

    def test_trigger_with_private_encrypted_channel_string_fail_case_no_encryption_master_key_specified(self):
        pc = PusherClient(app_id=u'4', key=u'key', secret=u'secret', ssl=True)

        with self.assertRaises(ValueError):
            pc.trigger(u'private-encrypted-tst', u'some_event', {u'message': u'hello worlds'})


    def test_trigger_with_public_channel_with_encryption_master_key_specified_success(self):
        json_dumped = u'{"message": "something"}'

        pc = PusherClient(
                app_id=u'4',
                key=u'key',
                secret=u'secret',
                encryption_master_key_base64=u'OHRXNUZRTG5pUTFzQlFGd3J3N3Q2VFZFc0paZDEweVk=',
                ssl=True)

        with mock.patch('json.dumps', return_value=json_dumped) as json_dumps_mock:

            request = pc.trigger.make_request(u'donuts', u'some_event', {u'message': u'hello worlds'})
            expected_params = {
                u'channels': [u'donuts'],
                u'data': json_dumped,
                u'name': u'some_event'
            }

            self.assertEqual(request.params, expected_params)

    def test_trigger_with_private_encrypted_channel_success(self):
        # instantiate a new client configured with the master encryption key
        master_key = b'8tW5FQLniQ1sBQFwrw7t6TVEsJZd10yY'
        master_key_base64 = base64.b64encode(master_key)
        pc = PusherClient(
                app_id=u'4',
                key=u'key',
                secret=u'secret',
                encryption_master_key_base64=master_key_base64,
                ssl=True)

        # trigger a request to a private-encrypted channel and capture the request to assert equality
        chan = "private-encrypted-tst"
        payload = {"message": "hello worlds"}
        event_name = 'some_event'
        request = pc.trigger.make_request(chan, event_name, payload)

        # simulate the same encryption process and check equality
        chan = ensure_binary(chan, "chan")
        shared_secret = generate_shared_secret(chan, master_key)

        box = nacl.secret.SecretBox(shared_secret)

        nonce_b64 = json.loads(request.params["data"])["nonce"].encode("utf-8")
        nonce = base64.b64decode(nonce_b64)

        encrypted = box.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf'-8"), nonce)

        # obtain the ciphertext
        cipher_text = encrypted.ciphertext

        # encode cipertext to base64
        cipher_text_b64 = base64.b64encode(cipher_text)

        # format expected output
        json_dumped = json.dumps({ "nonce" : nonce_b64.decode("utf-8"), "ciphertext": cipher_text_b64.decode("utf-8") })

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

    def test_trigger_disallow_private_encrypted_channel_with_multiple_channels(self):
        pc = PusherClient(
                app_id=u'4',
                key=u'key',
                secret=u'secret',
                encryption_master_key_base64=u'OHRXNUZRTG5pUTFzQlFGd3J3N3Q2VFZFc0paZDEweVk=',
                ssl=True)

        self.assertRaises(ValueError, lambda:
            self.pusher_client.trigger.make_request([u'my-chan', u'private-encrypted-pippo'], u'some_event', {u'message': u'hello world'}))

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
