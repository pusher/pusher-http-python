# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

from pusher.http import process_response

import requests
import sys
import os


if sys.version_info < (3,):
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()

CERT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/cacert.pem'


class RequestsBackend(object):
    """Adapter for the requests module.

    :param client:  pusher.Client object
    :param options: key-value passed into the requests.request constructor
    """
    def __init__(self, client, **options):
        self.client = client
        self.options = options
        if self.client.ssl:
            self.options.update({'verify': CERT_PATH})
        self.session = requests.Session()


    def send_request(self, request):
        resp = self.session.request(
            request.method,
            request.url,
            headers=request.headers,
            data=request.body,
            timeout=self.client.timeout,
            **self.options)

        return process_response(resp.status_code, resp.text)
