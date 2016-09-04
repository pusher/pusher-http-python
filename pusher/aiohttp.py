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
        self.conn = aiohttp.TCPConnector()


    def send_request(self, request):
        method = request.method
        url = "%s%s" % (request.base_url, request.path)
        params = request.query_params
        data = request.body
        headers = request.headers

        response = yield from asyncio.wait_for(
            aiohttp.request(
                method, url, params=params, data=data, headers=headers,
                connector=self.conn),
            timeout=self.client.timeout)

        body = yield from response.read_and_close()
        return process_response(response.status, body.decode('utf8'))
