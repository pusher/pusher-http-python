# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import six
import tornado
import tornado.httpclient

from tornado.concurrent import TracebackFuture

from pusher.http import process_response


class TornadoBackend(object):
    """Adapter for the tornado.httpclient module.

    :param client:  pusher.Client object
    :param kwargs:  options for the httpclient.HTTPClient constructor
    """
    def __init__(self, client, **kwargs):
        self.client = client
        self.http = tornado.httpclient.AsyncHTTPClient(**kwargs)


    def send_request(self, request):
        method = request.method
        data = request.body
        headers = {'Content-Type': 'application/json'}
        future = TracebackFuture()

        def process_response_future(response):
            if response.exc_info() is not None:
                future.set_exc_info(response.exc_info())

            elif response.exception() is not None:
                future.set_exception(response.exception())

            else:
                result = response.result()
                code = result.code
                body = (result.body or b'').decode('utf8')
                future.set_result(process_response(code, body))

        request = tornado.httpclient.HTTPRequest(
            request.url, method=method, body=data, headers=headers,
            request_timeout=self.client.timeout)

        response_future = self.http.fetch(request, raise_error=False)
        response_future.add_done_callback(process_response_future)

        return future
