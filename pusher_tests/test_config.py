# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import hashlib
import hmac
import os
import six
import unittest

from pusher import Pusher

try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestConfig(unittest.TestCase):
    def test_should_be_constructable(self):
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=False)

    def test_app_id_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=4, key=u'key', secret=u'secret', ssl=False))
        self.assertRaises(TypeError, lambda: Pusher(app_id=b'4', key=u'key', secret=u'secret', ssl=False))

    def test_key_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=4, secret=u'secret', ssl=False))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=b'key', secret=u'secret', ssl=False))

    def test_secret_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=4, ssl=False))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=b'secret', ssl=False))

    def test_ssl_should_be_required(self):
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=b'secret'))

    def test_ssl_should_be_boolean(self):
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True)

        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=4))

    def test_host_should_be_text(self):
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')

        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=b'foo'))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=4))

    def test_port_should_be_number(self):
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=400)

        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=u'400'))

    def test_cluster_should_be_text(self):
        Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')

        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=b'eu'))
        self.assertRaises(TypeError, lambda: Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=4))

    def test_host_behaviour(self):
        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
        self.assertEqual(conf.host, u'api.pusherapp.com', u'default host should be correct')

        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')
        self.assertEqual(conf.host, u'api-eu.pusher.com', u'host should be overriden by cluster setting')

        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')
        self.assertEqual(conf.host, u'foo', u'host should be overriden by host setting')

        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu', host=u'plah')
        self.assertEqual(conf.host, u'plah', u'host should be used in preference to cluster')

    def test_port_behaviour(self):
        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
        self.assertEqual(conf.port, 443, u'port should be 443 for ssl')

        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
        self.assertEqual(conf.port, 80, u'port should be 80 for non ssl')

        conf = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=False, port=4000)
        self.assertEqual(conf.port, 4000, u'the port setting override the default')

    def test_initialize_from_url(self):
        self.assertRaises(TypeError, lambda: Pusher.from_url(4))
        self.assertRaises(TypeError, lambda: Pusher.from_url(b'http://foo:bar@host/apps/4'))
        self.assertRaises(Exception, lambda: Pusher.from_url(u'httpsahsutaeh'))

        conf = Pusher.from_url(u'http://foo:bar@host/apps/4')
        self.assertEqual(conf.ssl, False)
        self.assertEqual(conf.key, u'foo')
        self.assertEqual(conf.secret, u'bar')
        self.assertEqual(conf.host, u'host')
        self.assertEqual(conf.app_id, u'4')

        conf = Pusher.from_url(u'https://foo:bar@host/apps/4')
        self.assertEqual(conf.ssl, True)
        self.assertEqual(conf.key, u'foo')
        self.assertEqual(conf.secret, u'bar')
        self.assertEqual(conf.host, u'host')
        self.assertEqual(conf.app_id, u'4')

if __name__ == '__main__':
    unittest.main()
