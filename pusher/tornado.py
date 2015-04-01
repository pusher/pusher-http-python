# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import tornado
import tornado.httpclient

class TornadoBackend(object):
    """Adapter for the tornado.httpclient module.

    :param config:  pusher.Pusher object
    """
    def __init__(self, config):
        if config.ssl:
            raise NotImplementedError("SSL not supported for this backend")
        self.config = config

    def send_request(self, request):
        method = request.method
        url = "http://%s:%s%s?%s" % (self.config.host, self.config.port, request.path, request.query_string)
        data = request.body
        headers = {'Content-Type': 'application/json'}

        return tornado.httpclient.HTTPRequest(url, method=method, body=data, request_timeout=self.config.timeout, headers=headers)
