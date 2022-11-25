# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import six

from pusher.util import ensure_text, ensure_binary, app_id_re
from pusher.crypto import parse_master_key


class Client(object):
    def __init__(
            self,
            app_id,
            key,
            secret,
            ssl=True,
            host=None,
            port=None,
            timeout=5,
            cluster=None,
            encryption_master_key=None,
            encryption_master_key_base64=None,
            json_encoder=None,
            json_decoder=None,
            backend=None,
            **backend_options):

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

        if host:
            self._host = ensure_text(host, "host")
        elif cluster:
            self._host = (
                six.text_type("api-%s.pusher.com") %
                ensure_text(cluster, "cluster"))
        else:
            self._host = six.text_type("api.pusherapp.com")

        if port and not isinstance(port, six.integer_types):
              raise TypeError("port should be an integer")

        self._port = port or (443 if ssl else 80)

        if not (isinstance(timeout, six.integer_types) or isinstance(timeout, float)):
              raise TypeError("timeout should be an integer or a float")

        self._timeout = timeout
        self._json_encoder = json_encoder
        self._json_decoder = json_decoder

        self._encryption_master_key = parse_master_key(encryption_master_key, encryption_master_key_base64)

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
