# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pusher
import unittest
import httpretty
import sys

@unittest.skipIf(sys.version_info >= (3,), "skip")
class TestURLFetchBackend(unittest.TestCase):

  def setUp(self):
    import pusher.urlfetch
    self.p = pusher.Pusher.from_url(u'http://key:secret@api.pusherapp.com/apps/4',
                                  backend=pusher.urlfetch.URLFetchBackend)

  @httpretty.activate
  def test_trigger_urlfetch_success(self):
    httpretty.register_uri(httpretty.POST, "http://api.pusherapp.com/apps/4/events",
                       body="{}",
                       content_type="application/json")
    response = self.p.trigger(u'test_channel', u'test', {u'data': u'yolo'})
    self.assertEqual(response, {})

if __name__ == '__main__':
    unittest.main()