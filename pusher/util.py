# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)

import json
import re
import six
import sys

channel_name_re = re.compile('^[-a-zA-Z0-9_=@,.;]+$')
app_id_re       = re.compile('^[0-9]+$')

if sys.version_info < (3,):
    text = 'a unicode string'
else:
    text = 'a string'

def validate_channel(channel):
    if not isinstance(channel, six.text_type):
        raise TypeError("Channel should be %s" % text)

    if len(channel) > 200:
        raise ValueError("Channel too long")

    if not channel_name_re.match(channel):
        raise ValueError("Invalid Channel: %s" % channel)
