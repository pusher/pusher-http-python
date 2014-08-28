# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division

import requests

from pusher.util import *

class RequestsBackend(object):
  def __init__(self, config, **options):
    self.options = {'verify': True}
    self.options.update(options)

  def send_request(self, request):
    resp = requests.request(
      request.method,
      request.url,
      headers=request.headers,
      data=request.body,
      **self.options
    )
    return process_response(resp.status_code, resp.text)
