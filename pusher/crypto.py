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
    data_to_string)

import nacl.secret
import nacl.utils

# The prefix any e2e channel must have
ENCRYPTED_PREFIX = 'private-encrypted-'

def is_encrypted_channel(channel):
    """
    is_encrypted_channel checks() if the channel is encrypted by verifying the prefix
    """
    if channel.startswith(ENCRYPTED_PREFIX):
        return True
    return False

def is_encryption_master_key_valid(encryption_master_key):
    """
    is_encryption_master_key_valid() checks if the provided encryption_master_key is validby checking its length
    """
    encryption_master_key = ensure_text(encryption_master_key, "encryption_master_key")
    if len(encryption_master_key) == 32:
        return True
    return False

def generate_shared_secret(channel, encryption_master_key):
    """
    generate_shared_secret() takes a utf8-string
    and returns the sha256 hash in utf8-string format
    """
    if is_encryption_master_key_valid(encryption_master_key):
        # the key has to be 32 bits long
        return hashlib.sha256( channel + encryption_master_key ).hexdigest()[:32]
    raise ValueError("Provided encryption_master_key is not 32 char long")

def encrypt(channel, data, encryption_master_key, nonce):
    """
    encrypt() encripts the provided payload specified in the 'data' parameter
    """
    shared_secret = generate_shared_secret(channel, encryption_master_key)

    # the box setup to seal/unseal data payload
    box = nacl.secret.SecretBox(shared_secret)

    """ this is here for reference the nonce
        it is currently passed to the function
        in order to allow testablity

        # generate the nonce with nacl
        #nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    """

    # convert nonce to base64
    nonce_b64 = base64.b64encode(nonce)

    # encrypt the data payload with nacl
    encrypted = box.encrypt(data, nonce)

    # obtain the ciphertext
    cipher_text = encrypted.ciphertext
    # encode cipertext to base64
    cipher_text_b64 = base64.b64encode(cipher_text)

    # format output
    return { "nonce" : nonce_b64, "ciphertext": cipher_text_b64 }

def decrypt():
    pass
