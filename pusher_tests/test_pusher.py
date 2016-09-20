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
        self.assertRaises(TypeError, lambda: Pusher.from_url(4))
        self.assertRaises(Exception, lambda: Pusher.from_url(u'httpsahsutaeh'))

        pusher = Pusher.from_url(u'http://foo:bar@host/apps/4')
        self.assertEqual(pusher._pusher_client.ssl, False)
        self.assertEqual(pusher._pusher_client.key, u'foo')
        self.assertEqual(pusher._pusher_client.secret, u'bar')
        self.assertEqual(pusher._pusher_client.host, u'host')
        self.assertEqual(pusher._pusher_client.app_id, u'4')

        pusher = Pusher.from_url(u'https://foo:bar@host/apps/4')
        self.assertEqual(pusher._pusher_client.ssl, True)
        self.assertEqual(pusher._pusher_client.key, u'foo')
        self.assertEqual(pusher._pusher_client.secret, u'bar')
        self.assertEqual(pusher._pusher_client.host, u'host')
        self.assertEqual(pusher._pusher_client.app_id, u'4')

    def test_initialize_from_env(self):
        with mock.patch.object(os, 'environ', new={'PUSHER_URL':'https://plah:bob@somehost/apps/42'}):
            pusher = Pusher.from_env()
            self.assertEqual(pusher._pusher_client.ssl, True)
            self.assertEqual(pusher._pusher_client.key, u'plah')
            self.assertEqual(pusher._pusher_client.secret, u'bob')
            self.assertEqual(pusher._pusher_client.host, u'somehost')
            self.assertEqual(pusher._pusher_client.app_id, u'42')


if __name__ == '__main__':
    unittest.main()
