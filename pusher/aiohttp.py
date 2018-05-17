# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import aiohttp
import asyncio

from pusher.http import process_response


class AsyncIOBackend:
    def __init__(self, client):
        """Adapter for the requests module.

        :param client:  pusher.Client object
        """
        self.client = client


    @asyncio.coroutine
    def send_request(self, request):
        session = response = None
        try:
            session = aiohttp.ClientSession()
            response = yield from session.request(
                request.method,
                "%s%s" % (request.base_url, request.path),
                params=request.query_params,
                data=request.body,
                headers=request.headers,
                timeout=self.client.timeout
            )
            body = yield from response.text('utf-8')
            return body
        finally:
            if response is not None:
                response.close()
            if session is not None:
                yield from session.close()
