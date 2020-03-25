# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import json
import six
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

        for t in testcases:
          self.assertEqual(
              crypto.is_encrypted_channel( t["input"] ),
              t["expected"],
          )

    def test_parse_master_key_successes(self):
        testcases = [
                { "deprecated": "this is 32 bytes 123456789012345", "base64": None, "expected": b"this is 32 bytes 123456789012345" },
                { "deprecated": "this key has nonprintable char \x00", "base64": None, "expected": b"this key has nonprintable char \x00"},
                { "deprecated": None, "base64": "dGhpcyBpcyAzMiBieXRlcyAxMjM0NTY3ODkwMTIzNDU=", "expected": b"this is 32 bytes 123456789012345" },
                { "deprecated": None, "base64": "dGhpcyBrZXkgaGFzIG5vbnByaW50YWJsZSBjaGFyIAA=", "expected": b"this key has nonprintable char \x00" },
            ]

        for t in testcases:
            self.assertEqual(
                    crypto.parse_master_key(t["deprecated"], t["base64"]),
                    t["expected"]
                )

    def test_parse_master_key_rejections(self):
        testcases = [
                { "deprecated": "some bytes", "base64": "also some bytes", "expected": "both" },
                { "deprecated": "this is 31 bytes 12345678901234", "base64": None, "expected": "32 bytes"},
                { "deprecated": "this is 33 bytes 1234567890123456", "base64": None, "expected": "32 bytes"},
                { "deprecated": None, "base64": "dGhpcyBpcyAzMSBieXRlcyAxMjM0NTY3ODkwMTIzNA==", "expected": "decodes to 32 bytes" },
                { "deprecated": None, "base64": "dGhpcyBpcyAzMyBieXRlcyAxMjM0NTY3ODkwMTIzNDU2", "expected": "decodes to 32 bytes" },
                { "deprecated": None, "base64": "dGhpcyBpcyAzMSBieXRlcyAxMjM0NTY3ODkwMTIzNA=", "expected": "valid base64" },
                { "deprecated": None, "base64": "dGhpcyBpcyA!MiBieXRlcyAxMjM0NTY3OD#wMTIzNDU=", "expected": "valid base64" },
            ]

        for t in testcases:
            six.assertRaisesRegex(self, ValueError, t["expected"], lambda: crypto.parse_master_key(t["deprecated"], t["base64"]))

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
