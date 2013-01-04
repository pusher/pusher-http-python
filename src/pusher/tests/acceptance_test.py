import unittest, re, httplib, time, cgi
from nose.tools import *

import sys
sys.path.append("../")

import pusher

try:
  import test_config
except ImportError:
  raise Exception("you must have a test_config.py file in order to run the acceptance tests. Rename test_config.example.py to test_config.py and add your credentials.")

class RequestTest(unittest.TestCase):

    def test_trigger(self):
      my_pusher = pusher.Pusher(app_id=test_config.app_id, key=test_config.app_key, secret=test_config.app_secret)
      channel = my_pusher['test-channel']
      result = channel.trigger('test-event', {'message': 'hello world'})
      
      eq_(result, True)
    
    def test_trigger_with_data_key_containing_percent(self):
      my_pusher = pusher.Pusher(app_id=test_config.app_id, key=test_config.app_key, secret=test_config.app_secret)
      channel = my_pusher['test-channel']
      result = channel.trigger('test-event', {'message %': 'hello world'})

      eq_(result, True)
      
    def test_trigger_with_data_value_containing_percent(self):
      my_pusher = pusher.Pusher(app_id=test_config.app_id, key=test_config.app_key, secret=test_config.app_secret)
      channel = my_pusher['test-channel']
      result = channel.trigger('test-event', {'message': "fish %"})

      eq_(result, True)