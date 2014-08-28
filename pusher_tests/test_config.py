# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import unittest
import os
import six
import time
import hmac
import hashlib

from pusher import Config

try:
  import unittest.mock as mock
except ImportError:
  import mock

class TestConfig(unittest.TestCase):
  def test_should_be_constructable(self):
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=False)

  def test_app_id_should_be_text(self):
    with self.assertRaises(TypeError):
      Config(key=u'key', secret=u'secret', ssl=False)

    with self.assertRaises(TypeError):
      Config(app_id=4, key=u'key', secret=u'secret', ssl=False)

    with self.assertRaises(TypeError):
      Config(app_id=b'4', key=u'key', secret=u'secret', ssl=False)

  def test_key_should_be_text(self):
    with self.assertRaises(TypeError):
      Config(app_id=u'4', secret=u'secret', ssl=False)

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=4, secret=u'secret', ssl=False)

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=b'key', secret=u'secret', ssl=False)

  def test_secret_should_be_text(self):
    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=4, ssl=False)

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=b'secret', ssl=False)

  def test_ssl_should_be_required(self):
    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=b'secret')

  def test_ssl_should_be_boolean(self):
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True)

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=4)

  def test_host_should_be_text(self):
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=b'foo')

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=4)

  def test_port_should_be_number(self):
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=400)

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, port=u'400')

  def test_cluster_should_be_text(self):
    Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=b'eu')

    with self.assertRaises(TypeError):
      Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=4)

  def test_host_behaviour(self):
    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
    self.assertEqual(conf.host, u'api.pusherapp.com', u'default host should be correct')

    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')
    self.assertEqual(conf.host, u'api-eu.pusher.com', u'host should be overriden by cluster setting')

    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, host=u'foo')
    self.assertEqual(conf.host, u'foo', u'host should be overriden by host setting')

    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu', host=u'plah')
    self.assertEqual(conf.host, u'plah', u'host should be used in preference to cluster')

  def test_port_behaviour(self):
    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=True)
    self.assertEqual(conf.port, 443, u'port should be 443 for ssl')

    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=False)
    self.assertEqual(conf.port, 80, u'port should be 80 for non ssl')

    conf = Config(app_id=u'4', key=u'key', secret=u'secret', ssl=False, port=4000)
    self.assertEqual(conf.port, 4000, u'the port setting override the default')

  def test_initialize_from_url(self):
    with self.assertRaises(TypeError):
      Config.from_url(4)

    with self.assertRaises(TypeError):
      Config.from_url(b'http://foo:bar@host/apps/4')

    with self.assertRaises(Exception):
      Config.from_url(u'httpsahsutaeh')

    conf = Config.from_url(u'http://foo:bar@host/apps/4')
    self.assertEqual(conf.ssl, False)
    self.assertEqual(conf.key, u'foo')
    self.assertEqual(conf.secret, u'bar')
    self.assertEqual(conf.host, u'host')
    self.assertEqual(conf.app_id, u'4')

    conf = Config.from_url(u'https://foo:bar@host/apps/4')
    self.assertEqual(conf.ssl, True)
    self.assertEqual(conf.key, u'foo')
    self.assertEqual(conf.secret, u'bar')
    self.assertEqual(conf.host, u'host')
    self.assertEqual(conf.app_id, u'4')

    with mock.patch.object(os, 'environ', new={'PUSHER_URL':'https://plah:bob@somehost/apps/42'}):
      conf = Config.from_url()
      self.assertEqual(conf.ssl, True)
      self.assertEqual(conf.key, u'plah')
      self.assertEqual(conf.secret, u'bob')
      self.assertEqual(conf.host, u'somehost')
      self.assertEqual(conf.app_id, u'42')

  def test_authenticate_subscription_types(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    with self.assertRaises(TypeError):
      conf.authenticate_subscription(b'plah', u'34554')

    with self.assertRaises(TypeError):
      conf.authenticate_subscription(u'plah', b'324435')

    with self.assertRaises(ValueError):
      conf.authenticate_subscription(u'::', u'345345')

  def test_authenticate_subscription_for_private_channels(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    expected = {
      u'auth': u"foo:076740bd063f0299742a73bc5aac88900e5f35cb0185a1facbf45d326b5b204b"
    }

    self.assertEqual(conf.authenticate_subscription(u'private-channel', u'34523'), expected)

  def test_authenticate_subscription_for_presence_channels(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    custom_data = {
      u'user_id': u'fred',
      u'user_info': {
        u'key': u'value'
      }
    }

    expected = {
      u'auth': u"foo:fbbc6d8acc85fc807bba060e2df45aba33deb8ad44cbee1633675b3ce73f4817",
      u'channel_data': u"{\"user_id\":\"fred\",\"user_info\":{\"key\":\"value\"}}"
    }

    with mock.patch('json.dumps', return_value=expected[u'channel_data']) as dumps_mock:
      actual = conf.authenticate_subscription(u'presence-channel', u'34543245', custom_data)

    self.assertEqual(actual, expected)
    dumps_mock.assert_called_once_with(custom_data)

  def test_validate_webhook_success_case(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    body = u'{"time_ms": 1000000}'
    signature = six.text_type(hmac.new(conf.secret.encode(u'utf8'), body.encode(u'utf8'), hashlib.sha256).hexdigest())

    with mock.patch('time.time', return_value=1200):
      self.assertEqual(conf.validate_webhook(conf.key, signature, body), {u'time_ms': 1000000})

  def test_validate_webhook_bad_types(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    conf.validate_webhook(u'key', u'signature', u'body')

    # These things are meant to be human readable, so enforcing being text is
    # sensible.

    with mock.patch('time.time') as time_mock:
      with self.assertRaises(TypeError):
        conf.validate_webhook(4, u'signature', u'body')

      with self.assertRaises(TypeError):
        conf.validate_webhook(b'test', u'signature', u'body')

      with self.assertRaises(TypeError):
        conf.validate_webhook(u'key', 4, u'body')

      with self.assertRaises(TypeError):
        conf.validate_webhook(u'key', b'signature', u'body')

      with self.assertRaises(TypeError):
        conf.validate_webhook(u'key', u'signature', 4)

      with self.assertRaises(TypeError):
        conf.validate_webhook(u'key', u'signature', b'body')

    time_mock.assert_not_called()

  def test_validate_webhook_bad_key(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    body = u'some body'
    signature = six.text_type(hmac.new(conf.secret.encode(u'utf8'), body.encode(u'utf8'), hashlib.sha256).hexdigest())

    with mock.patch('time.time') as time_mock:
      self.assertEqual(conf.validate_webhook(u'badkey', signature, body), None)

    time_mock.assert_not_called()

  def test_validate_webhook_bad_signature(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    body = u'some body'
    signature = u'some signature'

    with mock.patch('time.time') as time_mock:
      self.assertEqual(conf.validate_webhook(conf.key, signature, body), None)

    time_mock.assert_not_called()

  def test_validate_webhook_bad_time(self):
    conf = Config.from_url(u'http://foo:bar@host/apps/4')

    body = u'{"time_ms": 1000000}'
    signature = six.text_type(hmac.new(conf.secret.encode(u'utf8'), body.encode(u'utf8'), hashlib.sha256).hexdigest())

    with mock.patch('time.time', return_value=1301):
      self.assertEqual(conf.validate_webhook(conf.key, signature, body), None)

if __name__ == '__main__':
  unittest.main()
