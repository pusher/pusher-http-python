# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pusher
import httpretty
import sys
import os

if (sys.version_info < (2,7)):
  import unittest2 as unittest
else:
  import unittest

skip_test = (sys.version_info[0:2] != (2,7)) or os.environ.get("CI")

@unittest.skipIf(skip_test, "skip")
class TestGAEBackend(unittest.TestCase):

  def setUp(self):
    import pusher.gae
    from google.appengine.api import apiproxy_stub_map, urlfetch_stub

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',
    urlfetch_stub.URLFetchServiceStub())

    self.p = pusher.Pusher.from_url(u'http://key:secret@api.pusherapp.com/apps/4',
                                  backend=pusher.gae.GAEBackend)

  @httpretty.activate
  def test_trigger_gae_success(self):
    httpretty.register_uri(httpretty.POST, "http://api.pusherapp.com/apps/4/events",
                       body="{}",
                       content_type="application/json")
    response = self.p.trigger(u'test_channel', u'test', {u'data': u'yolo'})
    self.assertEqual(response, {})


if __name__ == '__main__':
    unittest.main()
