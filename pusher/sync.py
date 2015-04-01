# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.util import PusherError, process_response
from six.moves import http_client

import socket
import ssl
import sys

class SynchronousBackend(object):
    """Adapter for the standard-library http client.

    :param timeout: configurable timeout for the TCP connection
    """
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.http = None

    def send_request(self, config, request):
        if self.http is None:
            if config.ssl:
                ctx = ssl.create_default_context()
                self.http = http_client.HTTPSConnection(config.host, config.port, timeout=self.timeout, context=ctx)
            else:
                self.http = http_client.HTTPConnection(config.host, config.port, timeout=self.timeout)

        try:
            self.http.request(request.method, request.signed_path, request.body, {"Content-Type": "application/json"})
            resp = self.http.getresponse()
            body = resp.read().decode('utf8')
        except http_client.HTTPException as e:
            raise PusherError(repr(e))

        return process_response(resp.status, body)
