# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.errors import *
from pusher.signature import sign

import copy
import hashlib
import json
import six
import time

GET, POST, PUT, DELETE = "GET", "POST", "PUT", "DELETE"

class RequestMethod(object):
    def __init__(self, pusher, f):
        self.pusher = pusher
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.pusher.http.send_request(self.make_request(*args, **kwargs))

    def make_request(self, *args, **kwargs):
        return self.f(self.pusher, *args, **kwargs)

def doc_string(doc):
    def decorator(f):
        f.__doc__ = doc
        return f
    return decorator

def request_method(f):
    @property
    @doc_string(f.__doc__)
    def wrapped(self):
        return RequestMethod(self, f)
    return wrapped

def make_query_string(params):
    return '&'.join(map('='.join, sorted(params.items(), key=lambda x: x[0])))

def process_response(status, body):
    if status == 200:
        return json.loads(body)
    elif status == 400:
        raise PusherBadRequest(body)
    elif status == 401:
        raise PusherBadAuth(body)
    elif status == 403:
        raise PusherForbidden(body)
    else:
        raise PusherBadStatus("%s: %s" % (status, body))

class Request(object):
    """Represents the request to be made to the Pusher API.

    An instance of that object is passed to the backend's send_request method
    for each request.

    :param config: an instance of pusher.Pusher
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

        self.query_params['auth_signature'] = sign(self.config.secret, auth_string)

    @property
    def query_string(self):
        return make_query_string(self.query_params)

    @property
    def signed_path(self):
        return "%s?%s" % (self.path, self.query_string)

    @property
    def url(self):
        return "%s%s" % (self.base_url, self.signed_path)

    @property
    def base_url(self):
        return "%s://%s:%s" % (self.config.scheme, self.config.host, self.config.port)

    @property
    def headers(self):
        if self.method == POST:
            return {"Content-Type": "application/json"}
        else:
            return {}
