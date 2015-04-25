# -*- coding: utf-8 -*-

import hashlib
import hmac
import six

try:
    compare_digest = hmac.compare_digest
except AttributeError:
    # Not secure when the length is supposed to be kept secret
    def compare_digest(a, b):
        if len(a) != len(b):
            return False
        return reduce(lambda x, y: x | y, [ord(x) ^ ord(y) for x, y in zip(a, b)]) == 0

def sign(secret, string_to_sign):
    return six.text_type(
        hmac.new(
                secret.encode('utf8'),
                string_to_sign.encode('utf8'),
                hashlib.sha256
            )
            .hexdigest()
        )

def verify(secret, string_to_sign, signature):
    return compare_digest(signature, sign(secret, string_to_sign))
