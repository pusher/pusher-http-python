import unittest, re, httplib, time, cgi
from nose.tools import *
import mox

import sys
sys.path.append("../")

import socket
import pusher

class PropertiesTest(unittest.TestCase):
    def setUp(self):
        pusher.app_id = '123'
        pusher.key = 'test-global-key'
        pusher.secret = 'test-global-secret'

    def tearDown(self):
        pusher.app_id = None
        pusher.key = None
        pusher.secret = None


    #
    # Using globals
    #
    
    def test_global_app_id(self, *args):
        eq_(pusher.Pusher().app_id, '123')

    def test_global_key(self):
        eq_(pusher.Pusher().key, 'test-global-key')

    def test_global_secret(self):
        eq_(pusher.Pusher().secret, 'test-global-secret')


    #
    # Using instance-specific parameters
    #

    def test_instance_app_id(self):
        eq_(p().app_id, '456')

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

    def assert_request_is_correct(self, trigger_args, expected_query):
        request_args = ('POST', mox.Func(create_query_assertion(expected_query)), '{"param2": "value2", "param1": "value1"}', {'Content-Type': 'application/json'})
        stub_connection(self.mox, request_args=request_args)
        self.mox.ReplayAll()
        channel = p()['test-channel']
        channel.trigger(*trigger_args)
        self.mox.VerifyAll()

    def test_without_socket_id(self):
        trigger_args = (
            'test-event',
            {'param1': 'value1', 'param2': 'value2'},
        )
        expected_query = {
            'auth_version': '1.0',
            'auth_key': 'test-key',
            'auth_timestamp': '1272382015',
            'auth_signature': 'd34f60af4b4aeb17e018bec900e5395eb52ea2cb8b4272ce73e5003fc15ac353',
            'body_md5': 'd173e46bb2a4cf2d48a10bc13ec43d5a',
            'name': 'test-event',
        }
        self.assert_request_is_correct(trigger_args, expected_query)

    def test_with_socket_id(self):
        trigger_args = (
            'test-event',
            {'param1': 'value1', 'param2': 'value2'},
            'test-socket-id'
        )
        expected_query = {
            'auth_version': '1.0',
            'auth_key': 'test-key',
            'auth_timestamp': '1272382015',
            'auth_signature': 'a6751f6b09752da2aaf055910c600e0b7aeabf0f796b9b6cb4cd42ef30789675',
            'body_md5': 'd173e46bb2a4cf2d48a10bc13ec43d5a',
            'name': 'test-event',
            'socket_id': 'test-socket-id'
        }
        self.assert_request_is_correct(trigger_args, expected_query)

def create_query_assertion(expectation):
    def query_assertion(path_and_query):
        path, query_string = path_and_query.split('?')
        ok_(re.search('^/apps/456/channels/test-channel/events', path))
        for name, value in cgi.parse_qsl(query_string):
            eq_(value, expectation[name])
        return True
    return query_assertion

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

    def test_authenticate_socket(self):
        data = {'uid': 123, 'info': {'name': 'Foo'}}
        auth = self.channel.authenticate('socket_id', data)

        expected_auth = {'auth': 'test-key:3e976eef54ba057389c6530ac5a0c95d55043f4cf8013e47b99d20d9ce5144b4',
                         'channel_data': '{"info": {"name": "Foo"}, "uid": 123}'}
        eq_(auth, expected_auth)

    def test_authenticate_socket_with_no_data(self):
        data = {'uid': 123, 'info': {'name': 'Foo'}}
        auth = self.channel.authenticate('socket_id')

        expected_auth = {'auth': 'test-key:8ca017edcf179c9e6a5ff9708f630773bb0a367428c671cdf08972380400498e'}
        eq_(auth, expected_auth)


def stub_connection(moxer, request_args=None, response_status=202, body=''):
    moxer.StubOutWithMock(httplib.HTTPConnection, '__init__')
    httplib.HTTPConnection.__init__('api.pusherapp.com', 80, timeout=socket._GLOBAL_DEFAULT_TIMEOUT)

    moxer.StubOutWithMock(httplib.HTTPConnection, 'request')
    method_to_stub = httplib.HTTPConnection.request
    if request_args:
        method_to_stub(*request_args)
    else:
        method_to_stub(mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())

    moxer.StubOutWithMock(httplib.HTTPConnection, 'getresponse')
    mock_response = moxer.CreateMock(httplib.HTTPResponse)
    httplib.HTTPConnection.getresponse().AndReturn(mock_response)
    mock_response.status = response_status
    mock_response.read().AndReturn(body)
    moxer.StubOutWithMock(time, 'time')
    time.time().AndReturn(1272382015)

def p(*args):
    return pusher.Pusher(app_id='456', key='test-key', secret='test-secret')
