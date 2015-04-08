# -*- coding: utf-8 -*-

import aiohttp
import asyncio

from pusher.http import process_response

class AsyncIOBackend:
    def __init__(self, config):
        """Adapter for the requests module.

        :param config:  pusher.Pusher object
        """
        self.config = config
        self.conn = aiohttp.TCPConnector()

    def send_request(self, request):
        method = request.method
        url = "%s%s" % (request.base_url, request.path)
        params = request.query_params
        data = request.body
        headers = request.headers

        response = yield from asyncio.wait_for(
            aiohttp.request(method, url, params=params, data=data, headers=headers, connector=self.conn),
            timeout=self.config.timeout
        )
        body = yield from response.read_and_close()
        return process_response(response.status, body.decode('utf8'))
