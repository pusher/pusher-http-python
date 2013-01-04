import cgi
import httplib
import mox
import re
import time
import unittest
from nose.tools import eq_
from nose.tools import ok_
import pusher


class PusherTestCase(unittest.TestCase):
    """
    Base class with utilities that can be overridden, enabling reuse of tests
    for channel tests
    """
    @staticmethod
    def p(*args):
        return pusher.Pusher(app_id='test-app-id', key='test-key', secret='test-secret')

    @staticmethod
    def stub_connection(moxer, request_args=None, response_status=202):
        moxer.StubOutWithMock(httplib.HTTPConnection, '__init__')
        httplib.HTTPConnection.__init__('api.pusherapp.com', 80)

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
        moxer.StubOutWithMock(time, 'time')
        time.time().AndReturn(1272382015)


class PropertiesTest(PusherTestCase):
    #
    # Using instance-specific parameters, no globals support
    #
    def test_instance_app_id(self):
        eq_(self.p().app_id, 'test-app-id')

    def test_instance_key(self):
        eq_(self.p().key, 'test-key')

    def test_instance_secret(self):
        eq_(self.p().secret, 'test-secret')


class ChannelTest(PusherTestCase):
    def test_access_to_channels(self):
        channel = self.p()['test-channel']
        eq_(channel.__class__, pusher.Channel)
        eq_(channel.name, 'test-channel')

    def test_channel_name_verification(self):
        with self.assertRaises(ValueError) as cm:
            self.p()['di$@ll0w&d']
        eq_(cm.exception.message, 'Invalid chars: $&')


class RequestTest(PusherTestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def assert_request_is_correct(self, trigger_args, expected_query):
        request_args = ('POST', mox.Func(create_query_assertion(expected_query)), '{"param2": "value2", "param1": "value1"}', {'Content-Type': 'application/json'})
        self.stub_connection(self.mox, request_args=request_args)
        self.mox.ReplayAll()
        channel = self.p()['test-channel']
        channel.trigger(*trigger_args)
        self.mox.VerifyAll()

    def test_invalid_event_name(self):
        trigger_args = (
            '@vnt$',
            {'param1': 'value1', 'param2': 'value2'},
        )
        channel = self.p()['test-channel']
        with self.assertRaises(ValueError) as cm:
            channel.trigger(*trigger_args)
        eq_(cm.exception.message, 'Invalid chars: @$')

    def test_without_socket_id(self):
        trigger_args = (
            'test-event',
            {'param1': 'value1', 'param2': 'value2'},
        )
        expected_query = {
            'auth_version': '1.0',
            'auth_key': 'test-key',
            'auth_timestamp': '1272382015',
            'auth_signature': 'cf0b2a9890c2f0e2300f34d1c68efc8faad86b9d8ae35de1917d3b21176e5793',
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
            'auth_signature': 'be8985b730755f983224f23bcbe3be0876937b3bfe408014c19588435a8caffb',
            'body_md5': 'd173e46bb2a4cf2d48a10bc13ec43d5a',
            'name': 'test-event',
            'socket_id': 'test-socket-id'
        }
        self.assert_request_is_correct(trigger_args, expected_query)


def create_query_assertion(expectation):
    def query_assertion(path_and_query):
        path, query_string = path_and_query.split('?')
        ok_(re.search('^/apps/test-app-id/channels/test-channel/events', path))
        for name, value in cgi.parse_qsl(query_string):
            eq_(value, expectation[name])
        return True
    return query_assertion


class ResponsesTest(PusherTestCase):
    def setUp(self):
        self.mox = mox.Mox()
        self.channel = self.p()['test-channel']

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_trigger_gets_202_response(self):
        self.stub_connection(self.mox, response_status=202)
        self.mox.ReplayAll()
        ret = self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        eq_(ret, True)
        self.mox.VerifyAll()

    def test_trigger_gets_400_response(self):
        self.stub_connection(self.mox, response_status=400)
        self.mox.ReplayAll()
        with self.assertRaises(pusher.BadRequestError):
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

    def test_trigger_gets_401_response(self):
        self.stub_connection(self.mox, response_status=401)
        self.mox.ReplayAll()
        with self.assertRaises(pusher.AuthenticationError):
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

    def test_trigger_gets_403_response(self):
        self.stub_connection(self.mox, response_status=403)
        self.mox.ReplayAll()
        with self.assertRaises(pusher.ForbiddenError):
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

    def test_trigger_gets_404_response(self):
        self.stub_connection(self.mox, response_status=404)
        self.mox.ReplayAll()
        with self.assertRaises(pusher.NotFoundError):
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

    def test_trigger_gets_413_response(self):
        self.stub_connection(self.mox, response_status=413)
        self.mox.ReplayAll()
        with self.assertRaises(pusher.TooLargeError):
            self.channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

    def test_authenticate_socket(self):
        data = {'uid': 123, 'info': {'name': 'Foo'}}
        auth = self.channel.authenticate('socket_id', data)

        expected_auth = {'auth': 'test-key:3e976eef54ba057389c6530ac5a0c95d55043f4cf8013e47b99d20d9ce5144b4',
                         'channel_data': '{"info": {"name": "Foo"}, "uid": 123}'}
        eq_(auth, expected_auth)

    def test_authenticate_socket_with_no_data(self):
        auth = self.channel.authenticate('socket_id')

        expected_auth = {'auth': 'test-key:8ca017edcf179c9e6a5ff9708f630773bb0a367428c671cdf08972380400498e'}
        eq_(auth, expected_auth)
