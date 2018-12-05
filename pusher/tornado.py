# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import six
import tornado
import tornado.httpclient

from tornado.concurrent import Future

from pusher.http import process_response


class TornadoBackend(object):
    """Adapter for the tornado.httpclient module.

    :param client:   pusher.Client object
    :param options:  options for the httpclient.HTTPClient constructor
    """
    def __init__(self, client, **options):
        self.client = client
        self.options = options
        self.http = tornado.httpclient.AsyncHTTPClient()


    def send_request(self, request):
        method = request.method
        data = request.body
        headers = {'Content-Type': 'application/json'}
        future = Future()

        def process_response_future(response):
            if response.exception() is not None:
                future.set_exception(response.exception())

            else:
                result = response.result()
                code = result.code
                body = (result.body or b'').decode('utf8')
                future.set_result(process_response(code, body))

        request = tornado.httpclient.HTTPRequest(
            request.url,
            method=method,
            body=data,
            headers=headers,
            request_timeout=self.client.timeout,
            **self.options)

        response_future = self.http.fetch(request, raise_error=False)
        response_future.add_done_callback(process_response_future)

        return future
