import tornado.httpclient
from pusher import Channel


class TornadoChannel(Channel):
    """Tornado channel with callback"""
    def trigger(self, event, data={}, socket_id=None, callback=None):
        """
        Send event to pusher server

        Arguments:
            event: Event name sent to client
            data: Optional additional data to be sent to client, serialized as JSON
            socket_id: Optional socket id to specify sockets for channel
            callback: Callback to be called upon receiving response from pusher
        Returns:
            result of decide_outcome, True or exception
        """
        self.callback = callback
        return super(TornadoChannel, self).trigger(event, data, socket_id)

    def send_request(self, query_string, data_string):
        """
        Send async request to pusher server, registering callback

        Arguments:
            query_string: Query string included in URL
            data_string: HTTP body as JSON
        Returns:
            Fake http status code 202, actual error handling takes place in callback
        """
        secure = 's' if self.pusher.port == 443 else ''
        absolute_url = 'http%s://%s%s?%s' % (secure, self.pusher.host, self.path, query_string)
        request = tornado.httpclient.HTTPRequest(absolute_url, method='POST', body=data_string)
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, callback=self.callback)
        return 202  # Returning 202 to avoid Channel errors. Actual error handling takes place in callback.
