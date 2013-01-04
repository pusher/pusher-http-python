import logging
from google.appengine.ext import ndb
from pusher import Channel


class GoogleAppEngineChannel(Channel):
    @ndb.tasklet
    def trigger_async(self, event, data={}, socket_id=None):
        """
        Send event to pusher server async, yield while waiting for future result

        Arguments:
            event: Event name sent to client
            data: Optional additional data to be sent to client, serialized as JSON
            socket_id: Optional socket id to specify sockets for channel
        Returns:
            result of decide_outcome, True or exception
        """
        self.verify_event_name(event)
        json_data = self.pusher.json_dumps(data)
        status = yield self.send_request_async(self.signed_query(event, json_data, socket_id), json_data)
        result = self.decide_outcome(status)
        raise ndb.Return(result)

    @ndb.tasklet
    def send_request_async(self, query_string, data_string):
        """
        Send request to pusher server and yield while waiting for future result

        Arguments:
            query_string: Query string included in URL
            data_string: HTTP body as JSON
        Returns:
            HTTP status code int
        """
        ctx = ndb.get_context()
        secure = 's' if self.pusher.port == 443 else ''
        absolute_url = 'http%s://%s%s?%s' % (secure, self.pusher.host, self.path, query_string)
        result = yield ctx.urlfetch(
            url=absolute_url,
            payload=data_string,
            method='POST',
            headers={'Content-Type': 'application/json'},
            validate_certificate=bool(secure),
            )
        if result.status_code // 100 != 2:
            logging.debug('Code: %s\nBody\n%s' % (result.status_code, result.body))

        raise ndb.Return(result.status_code)

    def send_request(self, query_string, data_string):
        return self.send_request_async(query_string, data_string).get_result()
