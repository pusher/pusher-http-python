# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.util import app_id_re, channel_name_re, text

import hashlib
import hmac
import json
import os
import re
import six
import time

try:
  compare_digest = hmac.compare_digest
except AttributeError:
  # Not secure when the length is supposed to be kept secret
  def compare_digest(a, b):
    if len(a) != len(b):
      return False
    return reduce(lambda x, y: x | y, [ord(x) ^ ord(y) for x, y in zip(a, b)]) == 0

class Config(object):
  def __init__(self, app_id, key, secret, ssl, host=None, port=None, cluster=None):
    if not isinstance(app_id, six.text_type):
      raise TypeError("App ID should be %s" % text)

    if not isinstance(key, six.text_type):
      raise TypeError("Key should be %s" % text)

    if not isinstance(secret, six.text_type):
      raise TypeError("Secret should be %s" % text)

    if not app_id_re.match(app_id):
      raise ValueError("Invalid app id")

    if port and not isinstance(port, six.integer_types):
      raise TypeError("Port should be a number")

    if not isinstance(ssl, bool):
      raise TypeError("SSL should be a boolean")

    self.app_id = app_id
    self.key = key
    self.secret = secret

    if host:
      if not isinstance(host, six.text_type):
        raise TypeError("Host should be %s" % text)

      self.host = host
    elif cluster:
      if not isinstance(cluster, six.text_type):
        raise TypeError("Cluster should be %s" % text)

      self.host = "api-%s.pusher.com" % cluster
    else:
      self.host = "api.pusherapp.com"

    self.port = port or (443 if ssl else 80)
    self.ssl = ssl

  @classmethod
  def from_url(cls, url=None):
    url = url or six.text_type(os.environ['PUSHER_URL'])
    m = re.match("(http|https)://(.*):(.*)@(.*)/apps/([0-9]+)", url)
    if not m:
      raise Exception("Unparsable url: %s" % url)
    ssl = m.group(1) == 'https'
    return cls(key=m.group(2), secret=m.group(3), host=m.group(4), app_id=m.group(5), ssl=ssl)

  @property
  def scheme(self):
    return 'https' if self.ssl else 'http'

  def authenticate_subscription(self, channel, socket_id, custom_data=None):
    if not isinstance(channel, six.text_type):
      raise TypeError('Channel should be %s' % text)

    if not channel_name_re.match(channel):
      raise ValueError('Channel should be a valid channel, got: %s' % channel)

    if not isinstance(socket_id, six.text_type):
      raise TypeError('Socket ID should %s' % text)

    if custom_data:
      custom_data = json.dumps(custom_data)

    string_to_sign = "%s:%s" % (socket_id, channel)

    if custom_data:
      string_to_sign += ":%s" % custom_data

    signature = hmac.new(self.secret.encode('utf8'), string_to_sign.encode('utf8'), hashlib.sha256).hexdigest()

    auth = "%s:%s" % (self.key, signature)
    result = {'auth': auth}

    if custom_data:
      result['channel_data'] = custom_data

    return result

  def validate_webhook(self, key, signature, body):
    if not isinstance(key, six.text_type):
      raise TypeError('key should be %s' % text)

    if not isinstance(signature, six.text_type):
      raise TypeError('signature should be %s' % text)

    if not isinstance(body, six.text_type):
      raise TypeError('body should be %s' % text)

    if key != self.key:
      return None

    generated_signature = six.text_type(hmac.new(self.secret.encode('utf8'), body.encode('utf8'), hashlib.sha256).hexdigest())

    if not compare_digest(generated_signature, signature):
      return None

    try:
      body_data = json.loads(body)
    except ValueError:
      return None

    time_ms = body_data.get('time_ms')
    if not time_ms:
      return None

    print(abs(time.time()*1000 - time_ms))
    if abs(time.time()*1000 - time_ms) > 300000:
      return None

    return body_data
