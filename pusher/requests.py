# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.http import process_response

import requests

class RequestsBackend(object):
    """Adapter for the requests module.

    :param config:  pusher.Pusher object
    :param options: key-value passed into the requests.request constructor
    """
    def __init__(self, _, **options):
        self.options = {'verify': True}
        self.options.update(options)

    def send_request(self, request):
        resp = requests.request(
            request.method,
            request.url,
            headers=request.headers,
            data=request.body,
            **self.options
        )
        return process_response(resp.status_code, resp.text)
