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


if sys.version_info < (3,):
    byte_type = 'a python2 str'
else:
    byte_type = 'a python3 bytes' 

def ensure_text(obj, name):
    if isinstance(obj, six.text_type):
        return obj

    if isinstance(obj, six.string_types):
       return six.text_type(obj)

    if isinstance(obj, six.binary_type):
      return bytes(obj).decode('utf-8')

    raise TypeError("%s should be %s instead it is a %s" % (name, text, type(obj)))

def ensure_binary(obj, name):
    """
    ensure_binary() ensures that the value is a
    python2 str or python3 bytes
    more on this here: https://pythonhosted.org/six/#six.binary_type
    """
    if isinstance(obj, six.binary_type):
      return obj

    if isinstance(obj, six.text_type) or isinstance(obj, six.string_types):
       return obj.encode("utf-8")

    raise TypeError("%s should be %s instead it is a %s" % (name, byte_type, type(obj)))


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
