# -*- coding: utf-8 -*-

import aiohttp

from pusher.http import process_response

class AsyncIOBackend:
    def __init__(_, _):
        """Adapter for the requests module.

        :param config:  pusher.Pusher object
        """

    def send_request(_, request):
        method = request.method
        url = "%s%s" % (request.base_url, request.path)
        params = request.query_params
        data = request.body
        headers = request.headers

        response = yield from aiohttp.request(method, url, params=params, data=data, headers=headers)
        body = yield from response.read_and_close()
        return process_response(response.status, body.decode('utf8'))
