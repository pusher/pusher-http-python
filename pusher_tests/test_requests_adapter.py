# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pusher import Pusher
from unittest import mock
import certifi
import unittest
import httpretty
import sys

class TestRequestsBackend(unittest.TestCase):

  def setUp(self):

    # temporary ignoring warnings until these are sorted:
    # https://github.com/gabrielfalcao/HTTPretty/issues/368
    if sys.version_info[0] >= 3:
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed file <_io.BufferedRandom name*")

    self.pusher = Pusher.from_url(u'http://key:secret@api.pusherapp.com/apps/4')

  @httpretty.activate
  def test_trigger_requests_success(self):
    httpretty.register_uri(httpretty.POST, "http://api.pusherapp.com/apps/4/events",
                       body="{}",
                       content_type="application/json")
    response = self.pusher.trigger(u'test_channel', u'test', {u'data': u'yolo'})
    self.assertEqual(response, {})

  def _verify_option_sent_for(self, url):
    pusher = Pusher.from_url(url)
    response = mock.Mock(status_code=200, text="{}")
    with mock.patch("requests.Session.request", return_value=response) as request:
      pusher.trigger(u'test_channel', u'test', {u'data': u'yolo'})
    return request.call_args[1].get('verify')

  def test_ssl_requests_verify_against_certifi_bundle(self):
    verify = self._verify_option_sent_for(u'https://key:secret@api.pusherapp.com/apps/4')
    self.assertEqual(verify, certifi.where())

  def test_non_ssl_requests_do_not_set_verify(self):
    verify = self._verify_option_sent_for(u'http://key:secret@api.pusherapp.com/apps/4')
    self.assertIsNone(verify)


if __name__ == '__main__':
    unittest.main()
