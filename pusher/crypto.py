# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import hashlib
import nacl
import base64

from pusher.util import (
    ensure_text,
    ensure_binary,
    data_to_string)

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

def is_encryption_master_key_valid(encryption_master_key):
    """
    is_encryption_master_key_valid() checks if the provided encryption_master_key is valid by checking its length
    the key is assumed to be a six.binary_type (python2 str or python3 bytes)
    """
    if encryption_master_key is not None and len(encryption_master_key) == 32:
        return True

    return False

def generate_shared_secret(channel, encryption_master_key):
    """
    generate_shared_secret() takes a six.binary_type (python2 str or python3 bytes) channel name and encryption_master_key
    and returns the sha256 hash in six.binary_type format
    """
    if is_encryption_master_key_valid(encryption_master_key):
        # the key has to be 32 bytes long
        hashable = channel + encryption_master_key
        return hashlib.sha256(hashable).digest()

    raise ValueError("Provided encryption_master_key is not 32 char long")

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
