import unittest, re, httplib, time
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
        eq_(pusher.Pusher().app_id, 'test-global-app-id')

    def test_global_key(self):
        eq_(pusher.Pusher().key, 'test-global-key')

    def test_global_secret(self):
        eq_(pusher.Pusher().secret, 'test-global-secret')


    #
    # Using instance-specific parameters
    #

    def test_instance_app_id(self):
        eq_(p().app_id, 'test-app-id')

    def test_instance_key(self):
        eq_(p().key, 'test-key')

    def test_instance_secret(self):
        eq_(p().secret, 'test-secret')


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
        self.mox.StubOutWithMock(httplib.HTTPConnection, '__init__')
        httplib.HTTPConnection.__init__('api.pusherapp.com', 80)
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'request')
        httplib.HTTPConnection.request('POST', mox.Func(query_assertion), {'param2': 'value2', 'param1': 'value1'})
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'getresponse')
        httplib.HTTPConnection.getresponse().AndReturn(mock_response)
        self.mox.StubOutWithMock(time, 'time')
        time.time().AndReturn(1272382015)
        self.mox.ReplayAll()
        channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

def query_assertion(query):
    # '/apps/test-app-id/channels/test-channel/events?auth_version=1.0&auth_key=test-key&auth_timestamp=1272382015&auth_signature=0c9c750a1526e2c2a1f78aa56b758518c8261ffed0d8e3c6f5349e319610715c&body_md5=e7613e047876a84761546daf5fd9c3b6&name=test-event'
    return True

# http = httplib.HTTPConnection(self.api_host, self.api_port)
# http.request(verb, url, signed_data, headers)
# return http.getresponse().read()


def p(*args):
    return pusher.Pusher(app_id='test-app-id', key='test-key', secret='test-secret')
