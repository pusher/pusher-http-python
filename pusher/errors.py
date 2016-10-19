# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)


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
