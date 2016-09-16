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

from pusher.client import Client

try:
    import unittest.mock as mock

except ImportError:
    import mock


class TestClient(unittest.TestCase):
    def test_should_be_constructable(self):
        Client(app_id=u'4', key=u'key', secret=u'secret', ssl=False)


    def test_app_id_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Client(
            app_id=4, key=u'key', secret=u'secret', ssl=False))


    def test_key_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Client(
            app_id=u'4', key=4, secret=u'secret', ssl=False))


    def test_secret_should_be_text_if_present(self):
        self.assertRaises(TypeError, lambda: Client(
            app_id=u'4', key=u'key', secret=4, ssl=False))


    def test_ssl_should_be_boolean(self):
        Client(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
        Client(app_id=u'4', key=u'key', secret=u'secret', ssl=True)

        self.assertRaises(TypeError, lambda: Client(
            app_id=u'4', key=u'key', secret=u'secret', ssl=4))


    def test_port_should_be_number(self):
        Client(app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=400)

        self.assertRaises(TypeError, lambda: Client(
            app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=u'400'))


    def test_port_behaviour(self):
        conf = Client(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
        self.assertEqual(conf.port, 443, u'port should be 443 for ssl')

        conf = Client(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
        self.assertEqual(conf.port, 80, u'port should be 80 for non ssl')

        conf = Client(
            app_id=u'4', key=u'key', secret=u'secret', ssl=False, port=4000)

        self.assertEqual(
            conf.port, 4000, u'the port setting overrides the default')


if __name__ == '__main__':
    unittest.main()
