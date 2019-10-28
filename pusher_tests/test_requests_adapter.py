# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pusher import Pusher
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


if __name__ == '__main__':
    unittest.main()
