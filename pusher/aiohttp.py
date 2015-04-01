# -*- coding: utf-8 -*-

import aiohttp
import pusher

class AsyncIOBackend:
    def send_request(_, config, request):
        if config.ssl:
            raise NotImplementedError("SSL not supported for this backend")
        method = request.method
        url = "http://%s:%s%s" % (config.host, config.port, request.path)
        params = request.query_params
        data = request.body
        headers = request.headers

        response = yield from aiohttp.request(method, url, params=params, data=data, headers=headers)
        body = yield from response.read_and_close()
        return pusher.process_response(response.status, body.decode('utf8'))
