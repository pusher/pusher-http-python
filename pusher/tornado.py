# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import tornado
import tornado.httpclient

class TornadoBackend(object):
    def __init__(self, config, timeout=None):
        self.config = config
        self.timeout = timeout
        if self.config.ssl:
            raise NotImplementedError("SSL not supported for this backend")

    def send_request(self, request):
        method = request.method
        url = "http://%s:%s%s?%s" % (self.config.host, self.config.port, request.path, request.query_string)
        data = request.body
        headers = {'Content-Type': 'application/json'}

        return tornado.httpclient.HTTPRequest(url, method=method, body=data, request_timeout=self.timeout, headers=headers)
