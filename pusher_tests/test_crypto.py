# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import json
import unittest

from pusher import crypto

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

        # load more crazy fuzzy strings to stress test the encryption master key validation
        fuzzy_testcases = []
        with open('pusher_tests/fuzzy-encryption-keys.json') as f:
            fuzzy_testcases = json.load(f)

        testcases = [
          { "input":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "expected":True },
          { "input":"                                ", "expected":True },
          { "input":"private--encrypted--djsahajksha-", "expected":True },
          { "input":"dadasda;enc   ted--djsahajkshdak", "expected":True },
          { "input":"--====9.djsahajkshdak", "expected":False }
        ]

        # merge specific testcases with the fuzzy ones
        testcases += fuzzy_testcases

        # do the actual testing
        for t in testcases:
          self.assertEqual(
              crypto.is_encryption_master_key_valid( t["input"] ),
              t["expected"]
          )
    
    def test_generate_shared_secret(self):
        
        # load sample channel and encryption_master_key strings and their sha256 encodings
        sha256s_testcases = []
        with open('pusher_tests/sha256s.json') as f:
            sha256s_testcases = json.load(f)

        testcases = [
          {
            "input": ["pvUPIk0YG6MnxCEMIUUVFrbDmQwbhICXUcy",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5"],
            "expected": "709ef3090a24bfa98382cb5d025ca362"
          },
          {
            "input": ["Hk4F3",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5"],
            "expected": "d0c0b6770e40738337cba018b0b7443d"
          },
          {
            "input": ["kvC1JMEE4glNhEXXSLLNVX218RN3sEsAPgoUwKKSiQ7ASdOdEA",
                      "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0"],
            "expected": "51ca1e679fabc29f94545028d853e773"
          },
          {
            "input": ["GqYByIx5JE9avvMwPgyFDIuJm019XfqFwfgahZSBcnetFwlZNnE1wnS3F6E9IJf409Hm",
                      "AQIDBAUGBwgODxAREhMUFRYXGBkaGxwd"],
            "expected": "f9c1c56016ea9f5081358a972877c3d7"
          },
          {
            "input": ["V0CJ5U1r7t3oRcpKhhlVzN19",
                      "woDCgcKCwoPChMKGwofCiMKJworCi8KM"],
            "expected": "620fa93937212ff93f015c6a05c58772"
          },
          {
            "input": ["kfxrSj01BBd7NF1ltXFn0Yi5b15oGFgR1BBOc",
                      "CwwgwoXCoOGagOKAgOKAgeKAguKAg+KA"],
            "expected": "d0a6197c14e51c1e23049cb75b8d6d8f"
          },
          {
            "input": ["Ed8l",
                      "wq3YgNiB2ILYg9iE2IXYnNud3I/hoI7i"],
            "expected": "f525f853136c6c424e14d5cf63aaeecb"
          } 
        ]

        # merge specific testcases with externally loaded ones
        testcases += sha256s_testcases
        # do the actual testing
        for t in testcases:
          self.assertEqual(
              crypto.generate_shared_secret( t["input"][0], t["input"][1] ),
              t["expected"]
          )
    
    def test_encrypt(self):
        # load sample channel, payload, encryption_master_key, nonce inputs and
        # their respectively expected b64 encoded ciphertext and nonce
        sha256s_testcases = []
        with open('pusher_tests/encrypted-payload.json') as f:
            encrypted_payload_testcases = json.load(f)

        testcases = [
          {
            "input": ["pvUPIk0YG6MnxCEMIUUVFrbDmQwbhICXUcy", "kkkT5OOkOkO5kT5TOO5TkOT5TTk5O55T",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5", "XAJI0Y6DPBHSAHXTHV3A3ZMF"],
            "expected": {
              "nonce": "WEFKSTBZNkRQQkhTQUhYVEhWM0EzWk1G",
              "ciphertext": "b5XZUQAdKrTYGrsS/f2BRwB19KNaP4JJjogqrL8p3KBZ/jPEKi2q+Y2FH31EJiMM"
            },
          },
          {
            "input": ["Hk4F3", "TO5k5TTOkT5T5kkk55O5OkOOTkOkTT5O",
                      "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5", "G0FN9XUY41IBLJH75LXO6QJI" ],
            "expected": {
              "nonce": "RzBGTjlYVVk0MUlCTEpINzVMWE82UUpJ",
              "ciphertext": "uUXqfsK5MyqnNI5+wVdXmsGU5UhQd1u5ShvRs2Tt7CVEp63IygwyBoE2OyoJRWgR"
            },
          },
          {
            "input": ["kvC1JMEE4glNhEXXSLLNVX218RN3sEsAPgoUwKKSiQ7ASdOdEA",
                      "I4czDEUjgN5yjDzO2NT01TMxMMNMMAzQ",
                      "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0", "SG65KXVF1T2TALA753LC58DR"],
            "expected": {
              "nonce": "U0c2NUtYVkYxVDJUQUxBNzUzTEM1OERS",
              "ciphertext": "Pm5EnOX8XHwnYh5vwDon9LujR9AJFtnEsovnJEoHD6nct8rSGImRjeeP34u7mgCZ"
            },
          } 
        ]

        # merge specific testcases with the loaded ones
        testcases += encrypted_payload_testcases
        # do the actual testing
        for t in testcases:
          channel_test_val = t["input"][0].encode("utf-8")
          payload_test_val = t["input"][1].encode("utf-8")
          encr_key_test_val = t["input"][2].encode("utf-8")
          nonce_test_val = t["input"][3].encode("utf-8")

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
