# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import hashlib
import nacl
import base64
import binascii
import warnings

from pusher.util import (
    ensure_text,
    ensure_binary,
    data_to_string,
    is_base64)

import nacl.secret
import nacl.utils

# The prefix any e2e channel must have
ENCRYPTED_PREFIX = 'private-encrypted-'

def is_encrypted_channel(channel):
    """
    is_encrypted_channel() checks if the channel is encrypted by verifying the prefix
    """
    if channel.startswith(ENCRYPTED_PREFIX):
        return True
    return False

def parse_master_key(encryption_master_key, encryption_master_key_base64):
    """
    parse_master_key validates, parses and returns the bytes of the encryption master key
    from the constructor arguments.
    At present there is a deprecated "raw" key and a suggested base64 encoding.
    """
    if encryption_master_key is not None and encryption_master_key_base64 is not None:
        raise ValueError("Do not provide both encryption_master_key and encryption_master_key_base64. " +
                "encryption_master_key is deprecated, provide only encryption_master_key_base64")

    if encryption_master_key is not None:
        warnings.warn("`encryption_master_key` is deprecated, please use `encryption_master_key_base64`")
        if len(encryption_master_key) == 32:
            return ensure_binary(encryption_master_key, "encryption_master_key")
        else:
            raise ValueError("encryption_master_key must be 32 bytes long")

    if encryption_master_key_base64 is not None:
        if is_base64(encryption_master_key_base64):
            decoded = base64.b64decode(encryption_master_key_base64)

            if len(decoded) == 32:
                return decoded
            else:
                raise ValueError("encryption_master_key_base64 must be a base64 string which decodes to 32 bytes")
        else:
            raise ValueError("encryption_master_key_base64 must be valid base64")

    return None

def generate_shared_secret(channel, encryption_master_key):
    """
    generate_shared_secret() takes a six.binary_type (python2 str or python3 bytes) channel name and encryption_master_key
    and returns the sha256 hash in six.binary_type format
    """
    if encryption_master_key is None:
        raise ValueError("No master key was provided for use with encrypted channels. Please provide encryption_master_key_base64 as an argument to the Pusher SDK")

    hashable = channel + encryption_master_key
    return hashlib.sha256(hashable).digest()

def encrypt(channel, data, encryption_master_key, nonce=None):
    """
    encrypt() encrypts the provided payload specified in the 'data' parameter
    """
    channel = ensure_binary(channel, "channel")
    shared_secret = generate_shared_secret(channel, encryption_master_key)
    # the box setup to seal/unseal data payload
    box = nacl.secret.SecretBox(shared_secret)

    if nonce is None:
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    else:
        nonce = ensure_binary(nonce, "nonce")

    # convert nonce to base64
    nonce_b64 = base64.b64encode(nonce)

    # encrypt the data payload with nacl
    encrypted = box.encrypt(data.encode("utf-8"), nonce)

    # obtain the ciphertext
    cipher_text = encrypted.ciphertext
    # encode cipertext to base64
    cipher_text_b64 = base64.b64encode(cipher_text)

    # format output
    return { "nonce" : nonce_b64.decode("utf-8"), "ciphertext": cipher_text_b64.decode("utf-8") }
