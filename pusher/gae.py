# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

from google.appengine.api import urlfetch

from pusher.http import process_response


class GAEBackend(object):
    """
    Adapter for the URLFetch Module. Necessary for using this library with
    Google App Engine
    """
    def __init__(self, client, **options):
        self.client = client
        self.options = options


    def send_request(self, request):
        resp = urlfetch.fetch(
            url=request.url,
            headers=request.headers,
            method=request.method,
            payload=request.body,
            deadline=self.client.timeout,
            **self.options)

        return process_response(resp.status_code, resp.content)
