# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import json
import re
import six
import sys

channel_name_re = re.compile('^[-a-zA-Z0-9_=@,.;]+$')
app_id_re       = re.compile('^[0-9]+$')

GET, POST, PUT, DELETE = "GET", "POST", "PUT", "DELETE"

if sys.version_info < (3,):
    text = 'a unicode string'
else:
    text = 'a string'

class PusherError(Exception):
    pass

class PusherBadRequest(PusherError):
    pass

class PusherBadAuth(PusherError):
    pass

class PusherForbidden(PusherError):
    pass

class PusherBadStatus(PusherError):
    pass

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

def validate_channel(channel):
    if not isinstance(channel, six.text_type):
        raise TypeError("Channel should be %s" % text)

    if len(channel) > 200:
        raise ValueError("Channel too long")

    if not channel_name_re.match(channel):
        raise ValueError("Invalid Channel: %s" % channel)
