# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division

import socket
import six
import six.moves.http_client as http_client
import ssl

from pusher.util import *

class SynchronousBackend(object):
  def __init__(self, config, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    self.config = config
    self.timeout = timeout
    if config.ssl:
      if sys.version_info < (3,4):
        raise NotImplementedError("SSL requires python >= 3.4, earlier versions don't support certificate validation")

      ctx = ssl.create_default_context()
      self.http = http_client.HTTPSConnection(self.config.host, self.config.port, timeout=self.timeout, context=ctx)
    else:
      self.http = http_client.HTTPConnection(self.config.host, self.config.port, timeout=self.timeout)

  def send_request(self, request):
    try:
      self.http.request(request.method, request.signed_path, request.body, {"Content-Type": "application/json"})
      resp = self.http.getresponse()
      body = resp.read().decode('utf8')
    except http_client.HTTPException as e:
      raise PusherError(repr(e))

    return process_response(resp.status, body)
