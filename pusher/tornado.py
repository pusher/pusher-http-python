# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import tornado
import tornado.httpclient

class TornadoBackend(object):
    """Adapter for the tornado.httpclient module.

    :param config:  pusher.Pusher object
    :param kwargs:  options for the httpclient.HTTPClient constructor
    """
    def __init__(self, config, **kwargs):
        self.config = config
        self.http = httpclient.HTTPClient(**kwargs)

    def send_request(self, request):
        method = request.method
        data = request.body
        headers = {'Content-Type': 'application/json'}

        request = self.http.request.httpclient.HTTPRequest(request.url, method=method, body=data, headers=headers, request_timeout=self.config.timeout)
        return self.http.fetch(request, raise_error=False)
