# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.util import GET, POST
from pusher.signature import sign

import copy
import hashlib
import json
import six
import time

def make_query_string(params):
    return '&'.join(map('='.join, sorted(params.items(), key=lambda x: x[0])))

class Request(object):
    """Represents the request to be made to the Pusher API.

    An instance of that object is passed to the backend's send_request method
    for each request.

    :param config: an instance of pusher.Config
    :param method: HTTP method as a string
    :param path: The target path on the destination host
    :param params: Query params or body depending on the method
    """
    def __init__(self, config, method, path, params={}):
        self.config = config
        self.method = method
        self.path = path
        self.params = copy.copy(params)
        if method == POST:
            self.body = six.text_type(json.dumps(params)).encode('utf8')
            self.query_params = {}
        elif method == GET:
            self.body = bytes()
            self.query_params = params
        else:
            raise NotImplementedError("Only GET and POST supported")
        self._generate_auth()

    def _generate_auth(self):
        self.body_md5 = hashlib.md5(self.body).hexdigest()
        self.query_params.update({
            'auth_key': self.config.key,
            'body_md5': six.text_type(self.body_md5),
            'auth_version': '1.0',
            'auth_timestamp': '%.0f' % time.time()
        })

        auth_string = '\n'.join([
            self.method,
            self.path,
            make_query_string(self.query_params)
        ])

        secret = self.config.secret.encode('utf8')
        message = auth_string.encode('utf8')

        self.query_params['auth_signature'] = sign(secret, message)

    @property
    def query_string(self):
        return make_query_string(self.query_params)

    @property
    def signed_path(self):
        return "%s?%s" % (self.path, self.query_string)

    @property
    def url(self):
        return "%s://%s:%s%s" % (self.config.scheme, self.config.host, self.config.port, self.signed_path)

    @property
    def headers(self):
        if self.method == POST:
            return {"Content-Type": "application/json"}
        else:
            return {}
