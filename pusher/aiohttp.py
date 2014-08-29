# -*- coding: utf-8 -*-

import aiohttp
import pusher

class AsyncIOBackend:
    """Adapter for the aiohttp module.

    This backend is only availble for python 3 users and doesn't support SSL.

    :param config: pusher.Config instance
    """
    def __init__(self, config):
        self.config = config
        if config.ssl:
            raise NotImplementedError("SSL not supported for this backend")

    def send_request(self, request):
        method = request.method
        url = "http://%s:%s%s" % (self.config.host, self.config.port, request.path)
        params = request.query_params
        data = request.body
        headers = request.headers

        response = yield from aiohttp.request(method, url, params=params, data=data, headers=headers)
        body = yield from response.read_and_close()
        return pusher.process_response(response.status, body.decode('utf8'))
