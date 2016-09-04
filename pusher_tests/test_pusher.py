# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import hashlib
import hmac
import os
import six
import unittest

from pusher.pusher import Pusher

try:
    import unittest.mock as mock
except ImportError:
    import mock


class TestPusher(unittest.TestCase):
    def test_initialize_from_url(self):
        self.assertRaises(TypeError, lambda: Client.from_url(4))
        self.assertRaises(Exception, lambda: Client.from_url(u'httpsahsutaeh'))

        conf = Client.from_url(u'http://foo:bar@host/apps/4')
        self.assertEqual(conf.ssl, False)
        self.assertEqual(conf.key, u'foo')
        self.assertEqual(conf.secret, u'bar')
        self.assertEqual(conf.host, u'host')
        self.assertEqual(conf.app_id, u'4')

        conf = Client.from_url(u'https://foo:bar@host/apps/4')
        self.assertEqual(conf.ssl, True)
        self.assertEqual(conf.key, u'foo')
        self.assertEqual(conf.secret, u'bar')
        self.assertEqual(conf.host, u'host')
        self.assertEqual(conf.app_id, u'4')

    def test_initialize_from_env(self):
        with mock.patch.object(os, 'environ', new={'PUSHER_URL':'https://plah:bob@somehost/apps/42'}):
            pusher = Pusher.from_env()
            self.assertEqual(pusher.ssl, True)
            self.assertEqual(pusher.key, u'plah')
            self.assertEqual(pusher.secret, u'bob')
            self.assertEqual(pusher.host, u'somehost')
            self.assertEqual(pusher.app_id, u'42')


class TestJson(unittest.TestCase):
    def setUp(self):
        class JSONEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Decimal):
                    return str(o)
                return super(JSONEncoder, self).default(o)

        constants = {"NaN": 99999}

        class JSONDecoder(json.JSONDecoder):
            def __init__(self, **kwargs):
                super(JSONDecoder, self).__init__(parse_constant=constants.__getitem__)

        self.pusher_client = PusherClient.from_url(u'http://key:secret@somehost/apps/4',
                                      json_encoder=JSONEncoder,
                                      json_decoder=JSONDecoder)

    def test_custom_json_decoder(self):
        t = 1000 * time.time()
        body = u'{"nan": NaN, "time_ms": %f}' % t
        signature = sign(self.pusher_client.secret, body)
        data = self.pusher_client.validate_webhook(self.pusher_client.key, signature, body)
        self.assertEqual({u"nan": 99999, u"time_ms": t}, data)

    def test_custom_json_encoder(self):
        expected = {
            u'channel_data': '{"money": "1.32"}',
            u'auth': u'key:7f2ae5922800a20b9615543ce7c8e7d1c97115d108939410825ea690f308a05f'
        }
        data = self.pusher_client.authenticate("presence-c1", "1.1", {"money": Decimal("1.32")})
        self.assertEqual(expected, data)
