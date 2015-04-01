# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import tornado
import tornado.httpclient

class TornadoBackend(object):
    """Adapter for the tornado.httpclient module.

    :param timeout: configurable timeout for the connection
    """
    def __init__(self, timeout=None):
        self.timeout = timeout

    def send_request(self, config, request):
        if config.ssl:
            raise NotImplementedError("SSL not supported for this backend")
        method = request.method
        url = "http://%s:%s%s?%s" % (config.host, config.port, request.path, request.query_string)
        data = request.body
        headers = {'Content-Type': 'application/json'}

        return tornado.httpclient.HTTPRequest(url, method=method, body=data, request_timeout=self.timeout, headers=headers)
