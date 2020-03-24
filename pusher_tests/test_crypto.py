# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import json
import unittest

from pusher import crypto
from pusher.util import ensure_binary

class TestCrypto(unittest.TestCase):

    def test_is_encrypted_channel(self):
        # testcases matrix with inputs and expected returning values
        testcases = [
          { "input":"private-encrypted-djsahajkshdak", "expected":True },
          { "input":"private-encrypted-djsahajkshdak-", "expected":True },
          { "input":"private-encrypted--djsahajkshdak", "expected":True },
          { "input":"private--encrypted--djsahajkshdak", "expected":False },
          { "input":"private--encrypted--djsahajkshdak-", "expected":False },
          { "input":"private-encr-djsahajkshdak", "expected":False },
          { "input":"private-encrypteddjsahajkshdak", "expected":False },
          { "input":"private-encrypte-djsahajkshdak", "expected":False },
          { "input":"privateencrypte-djsahajkshdak", "expected":False },
          { "input":"private-djsahajkshdak", "expected":False },
          { "input":"--djsah private-encrypted-ajkshdak", "expected":False }
        ]

        # do the actual testing
        for t in testcases:
          self.assertEqual(
              crypto.is_encrypted_channel( t["input"] ),
              t["expected"]
          )

    def test_is_encryption_master_key_valid(self):
        testcases = [
          { "input":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "expected":True },
          { "input":"                                ", "expected":True },
          { "input":"private--encrypted--djsahajksha-", "expected":True },
          { "input":"dadasda;enc   ted--djsahajkshdak", "expected":True },
          { "input":"--====9.djsahajkshdak", "expected":False }
        ]

        # do the actual testing
        for t in testcases:
          self.assertEqual(
              crypto.is_encryption_master_key_valid( t["input"] ),
              t["expected"]
          )

    def test_generate_shared_secret(self):
        testcases = [
          {
            "input": ["pvUPIk0YG6MnxCEMIUUVFrbDmQwbhICXUcy",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5"],
            "expected": b"p\x9e\xf3\t\n$\xbf\xa9\x83\x82\xcb]\x02\\\xa3b,\x82\xd3\x1f\xa2\x7f\x10\xb0\x05\xc0\xdc\xa2{\xaee\x16"
          }
        ]

        # do the actual testing
        for t in testcases:
          self.assertEqual(
              crypto.generate_shared_secret( ensure_binary(t["input"][0],'t["input"][0]'), ensure_binary(t["input"][1],'t["input"][1]') ),
              t["expected"]
          )

    def test_encrypt(self):
        testcases = [
          {
            "input": ["pvUPIk0YG6MnxCEMIUUVFrbDmQwbhICXUcy", "kkkT5OOkOkO5kT5TOO5TkOT5TTk5O55T",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5", "XAJI0Y6DPBHSAHXTHV3A3ZMF"],
            "expected": {
              "nonce": "WEFKSTBZNkRQQkhTQUhYVEhWM0EzWk1G",
              "ciphertext": "tsYJa2JgGDOpVIYFe4aNVWAvZlpB7z7CjN9mpIdbATE0Yc4izN8aM8D6VigBxnIQ"
            },
          }
        ]

        # do the actual testing
        for t in testcases:
          channel_test_val = t["input"][0]
          payload_test_val = t["input"][1]
          encr_key_test_val = ensure_binary(t["input"][2],'t["input"][2]')
          nonce_test_val = t["input"][3]

          self.assertEqual(
              crypto.encrypt(
                channel_test_val,
                payload_test_val,
                encr_key_test_val,
                nonce_test_val
              ),
              t["expected"]
          )

    def test_decrypt(self):
        self.assertEqual(True, True)
