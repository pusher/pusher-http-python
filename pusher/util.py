# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import json
import re
import six
import sys


channel_name_re = re.compile('\A[-a-zA-Z0-9_=@,.;]+\Z')
app_id_re = re.compile('\A[0-9]+\Z')
pusher_url_re = re.compile('\A(http|https)://(.*):(.*)@(.*)/apps/([0-9]+)\Z')
socket_id_re = re.compile('\A\d+\.\d+\Z')

if sys.version_info < (3,):
    text = 'a unicode string'
else:
    text = 'a string'


def ensure_text(obj, name):
    if isinstance(obj, six.text_type):
        return obj

    if isinstance(obj, six.string_types):
       return six.text_type(obj)

    raise TypeError("%s should be %s" % (name, text))


def validate_channel(channel):
    channel = ensure_text(channel, "channel")

    if len(channel) > 200:
        raise ValueError("Channel too long: %s" % channel)

    if not channel_name_re.match(channel):
        raise ValueError("Invalid Channel: %s" % channel)

    return channel


def validate_socket_id(socket_id):
    socket_id = ensure_text(socket_id, "socket_id")

    if not socket_id_re.match(socket_id):
        raise ValueError("Invalid socket ID: %s" % socket_id)

    return socket_id


def join_attributes(attributes):
    return six.text_type(',').join(attributes)


def data_to_string(data, json_encoder):
    if isinstance(data, six.string_types):
        return ensure_text(data, "data")

    else:
        return json.dumps(data, cls=json_encoder)


def doc_string(doc):
    def decorator(f):
        f.__doc__ = doc
        return f

    return decorator
