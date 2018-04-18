# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import unittest
import re
import sys

from pusher import Pusher
from pusher.http import Request

try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestRequest(unittest.TestCase):
    def test_get_signature_generation(self):
        conf = Pusher.from_url(u'http://key:secret@somehost/apps/4')

        expected = {
            u'auth_key': u'key',
            u'auth_signature': u'5c49f04a95eedc9028b1e0e8de7c2c7ad63504a0e3b5c145d2accaef6c14dbac',
            u'auth_timestamp': u'1000',
            u'auth_version': u'1.0',
            u'body_md5': u'd41d8cd98f00b204e9800998ecf8427e',
            u'foo': u'bar'
        }

        with mock.patch('time.time', return_value=1000):
            req = Request(conf._pusher_client, u'GET', u'/some/obscure/api', {u'foo': u'bar'})
            self.assertEqual(req.query_params, expected)

    def test_post_signature_generation(self):
        conf = Pusher.from_url(u'http://key:secret@somehost/apps/4')

        expected = {
            u'auth_key': u'key',
            u'auth_signature': u'e05fa4cafee86311746ee3981d5581a5e4e87c27bbab0aeb1059e2df5c90258b',
            u'auth_timestamp': u'1000',
            u'auth_version': u'1.0',
            u'body_md5': u'94232c5b8fc9272f6f73a1e36eb68fcf'
        }

        with mock.patch('time.time', return_value=1000):
            # patching this, because json can be unambiguously parsed, but not
            # unambiguously generated (think whitespace).
            with mock.patch('json.dumps', return_value='{"foo": "bar"}') as json_dumps_mock:
                req = Request(conf._pusher_client, u'POST', u'/some/obscure/api', {u'foo': u'bar'})
                self.assertEqual(req.query_params, expected)

            json_dumps_mock.assert_called_once_with({u"foo": u"bar"})

    def test_x_pusher_library_header(self):
        conf = Pusher.from_url(u'http://key:secret@somehost/apps/4')
        req = Request(conf._pusher_client, u'GET', u'/some/obscure/api', {u'foo': u'bar'})
        self.assertTrue('X-Pusher-Library' in req.headers)
        pusherLib = req.headers['X-Pusher-Library']
        regex = r'^pusher-http-python \d+(\.\d+)+(rc\d+)?$'
        if sys.version_info < (3,):
            self.assertRegexpMatches(pusherLib, regex)
        else:
            self.assertRegex(pusherLib, regex)

if __name__ == '__main__':
    unittest.main()
