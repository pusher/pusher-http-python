# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import six

from pusher.util import ensure_text, app_id_re


class Client(object):
    def __init__(
            self, app_id, key, secret, ssl=True, host=None, port=None,
            timeout=5, cluster=None, json_encoder=None, json_decoder=None,
            backend=None, **backend_options):
        if backend is None:
              from .requests import RequestsBackend
              backend = RequestsBackend

        self._app_id = ensure_text(app_id, "app_id")
        if not app_id_re.match(self._app_id):
              raise ValueError("Invalid app id")

        self._key = ensure_text(key, "key")
        self._secret = ensure_text(secret, "secret")

        if not isinstance(ssl, bool):
              raise TypeError("SSL should be a boolean")

        self._ssl = ssl

        if port and not isinstance(port, six.integer_types):
              raise TypeError("port should be an integer")

        self._port = port or (443 if ssl else 80)

        if not isinstance(timeout, six.integer_types):
              raise TypeError("timeout should be an integer")

        self._timeout = timeout
        self._json_encoder = json_encoder
        self._json_decoder = json_decoder

        self.http = backend(self, **backend_options)

    @property
    def app_id(self):
        return self._app_id

    @property
    def key(self):
        return self._key

    @property
    def secret(self):
        return self._secret

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def timeout(self):
        return self._timeout

    @property
    def ssl(self):
        return self._ssl

    @property
    def scheme(self):
        return 'https' if self.ssl else 'http'
