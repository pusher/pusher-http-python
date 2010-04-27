import unittest, re, httplib
from nose.tools import *
import mox
import pusher

class PropertiesTest(unittest.TestCase):
    def setUp(self):
        pusher.app_id = 'test-global-app-id'
        pusher.key = 'test-global-key'
        pusher.secret = 'test-global-secret'

    def tearDown(self):
        pusher.app_id = 'api.pusherapp.com'
        pusher.key = None
        pusher.secret = None


    #
    # Using globals
    #

    def test_global_app_id(self, *args):
        eq_(p().app_id, 'test-global-app-id')

    def test_global_key(self):
        eq_(p().key, 'test-global-key')

    def test_global_secret(self):
        eq_(p().secret, 'test-global-secret')


    #
    # Using instance-specific parameters
    #

    def _instance(*args):
        return pusher.Pusher(app_id='test-instance-app-id', key='test-instance-key', secret='test-instance-secret')

    def test_instance_app_id(self):
        eq_(self._instance().app_id, 'test-instance-app-id')

    def test_instance_key(self):
        eq_(self._instance().key, 'test-instance-key')

    def test_instance_secret(self):
        eq_(self._instance().secret, 'test-instance-secret')


class ChannelTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_access_to_channels(self):
        channel = p()['test-channel']
        eq_(channel.__class__, pusher.Channel)
        eq_(channel.name, 'test-channel')

    def test_trigger(self):
        channel = p()['test-channel']
        mock_response = self.mox.CreateMock(httplib.HTTPResponse)
        mock_response.read()
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'request')
        httplib.HTTPConnection.request('POST', 'http://staging.api.pusherapp.com/app/None/channel/test-channel')
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'getresponse')
        httplib.HTTPConnection.getresponse().AndReturn(mock_response)
        self.mox.ReplayAll()
        channel.trigger()
        self.mox.VerifyAll()

def p(*args):
    return pusher.Pusher(*args)
