import unittest, re, httplib, time, cgi
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
    def test_access_to_channels(self):
        channel = p()['test-channel']
        eq_(channel.__class__, pusher.Channel)
        eq_(channel.name, 'test-channel')

class RequestTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_it(self):
        request_args = ('POST', mox.Func(query_assertion), '{"param2": "value2", "param1": "value1"}')
        stub_connection(self.mox, request_args=request_args)
        self.mox.ReplayAll()
        channel = p()['test-channel']
        channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

def query_assertion(path_and_query):
    path, query_string = path_and_query.split('?')
    ok_(re.search('^/apps/test-app-id/channels/test-channel/events', path))
    expected_query = {
        'auth_version': '1.0',
        'auth_key': 'test-key',
        'auth_timestamp': '1272382015',
        'auth_signature': 'cf0b2a9890c2f0e2300f34d1c68efc8faad86b9d8ae35de1917d3b21176e5793',
        'body_md5': 'd173e46bb2a4cf2d48a10bc13ec43d5a',
        'name': 'test-event',
    }

    for name, value in cgi.parse_qsl(query_string):
        eq_(value, expected_query[name])
    return True

class ResponsesTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        self.channel = p()['test-channel']

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_trigger_gets_202_response(self):
        stub_connection(self.mox, response_status=202)
        self.mox.ReplayAll()
        ret = self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        eq_(ret, True)
        self.mox.VerifyAll()

    def test_trigger_gets_401_response(self):
        stub_connection(self.mox, response_status=401)
        self.mox.ReplayAll()
        try:
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        except pusher.AuthenticationError:
            ok_(True)
        else:
            ok_(False, "Expected an AuthenticationError")
        self.mox.VerifyAll()

    def test_trigger_gets_404_response(self):
        stub_connection(self.mox, response_status=404)
        self.mox.ReplayAll()
        try:
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        except pusher.NotFoundError:
            ok_(True)
        else:
            ok_(False, "Expected a NotFoundError")
        self.mox.VerifyAll()

def stub_connection(moxer, request_args=None, response_status=202):
    moxer.StubOutWithMock(httplib.HTTPConnection, '__init__')
    httplib.HTTPConnection.__init__('api.pusherapp.com', 80)

    moxer.StubOutWithMock(httplib.HTTPConnection, 'request')
    method_to_stub = httplib.HTTPConnection.request
    if request_args:
        method_to_stub(*request_args)
    else:
        method_to_stub(mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())

    moxer.StubOutWithMock(httplib.HTTPConnection, 'getresponse')
    mock_response = moxer.CreateMock(httplib.HTTPResponse)
    httplib.HTTPConnection.getresponse().AndReturn(mock_response)
    mock_response.status = response_status
    moxer.StubOutWithMock(time, 'time')
    time.time().AndReturn(1272382015)

def p(*args):
    return pusher.Pusher(app_id='test-app-id', key='test-key', secret='test-secret')
