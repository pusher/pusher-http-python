# -*- coding: utf-8 -*-

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