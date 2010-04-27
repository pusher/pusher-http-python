import unittest, re
from nose.tools import *
import pusher

class PropertiesTest(unittest.TestCase):
    def setUp(self):
        pusher.app_id = 'test-global-app-id'
        pusher.key = 'test-global-key'
        pusher.secret = 'test-global-secret'
        self.i = pusher.Pusher()

    def tearDown(self):
        pusher.app_id = 'api.pusherapp.com'
        pusher.key = None
        pusher.secret = None

    def test_global_app_id(self):
        eq_(self.i.app_id, 'test-global-app-id')

    def test_global_key(self):
        eq_(self.i.key, 'test-global-key')

    def test_global_secret(self):
        eq_(self.i.secret, 'test-global-secret')

