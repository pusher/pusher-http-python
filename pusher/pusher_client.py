# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division)

import sys
# Abstract Base Classes were moved into collections.abc in Python 3.3
if sys.version_info >= (3,3):
    import collections.abc as collections
else:
    import collections
import hashlib
import os
import re
import six
import time
import json
import string

from pusher.util import (
    ensure_text,
    validate_channel,
    validate_socket_id,
    join_attributes,
    data_to_string)

from pusher.client import Client
from pusher.http import GET, POST, Request, request_method
from pusher.crypto import *
import random
from datetime import datetime


class PusherClient(Client):
    def __init__(
            self, app_id, key, secret, ssl=True,
            host=None, port=None,
            timeout=5, cluster=None,
            encryption_master_key=None,
            json_encoder=None, json_decoder=None,
            backend=None, max_num_channels = None,
            max_len_event_name = None, max_len_data = None, **backend_options):
        super(PusherClient, self).__init__(
            app_id, key, secret, ssl, host, port, timeout, cluster,
            encryption_master_key, json_encoder, json_decoder,
            backend, **backend_options)

        self.max_num_channels = max_num_channels if max_num_channels is not None else 100
        self.max_len_event_name = max_len_event_name if max_len_event_name is not None else 200
        self.max_len_data = max_len_data if max_len_data is not None else 10240

        if host:
            self._host = ensure_text(host, "host")

        elif cluster:
            self._host = (
                six.text_type("api-%s.pusher.com") %
                ensure_text(cluster, "cluster"))
        else:
            self._host = six.text_type("api.pusherapp.com")


    @request_method
    def trigger(self, channels, event_name, data, socket_id=None):
        """Trigger an event on one or more channels, see:

        http://pusher.com/docs/rest_api#method-post-event
        """
        if isinstance(channels, six.string_types):
            channels = [channels]

        if isinstance(channels, dict) or not isinstance(
                channels, (collections.Sized, collections.Iterable)):
            raise TypeError("Expected a single or a list of channels")

        if len(channels) > self.max_num_channels:
            raise ValueError("Too many channels")

        event_name = ensure_text(event_name, "event_name")
        if len(event_name) > self.max_len_event_name:
            raise ValueError("event_name too long")

        data = data_to_string(data, self._json_encoder)
        if len(data) > self.max_len_data:
            raise ValueError("Too much data")

        channels = list(map(validate_channel, channels))

        if len(channels) > 1:
            for chan in channels:
                if is_encrypted_channel(chan):
                    raise ValueError("You cannot trigger to multiple channels when using encrypted channels")

        if is_encrypted_channel(channels[0]):
            data = json.dumps(encrypt(channels[0], data, self._encryption_master_key), ensure_ascii=False)

        params = {
            'name': event_name,
            'channels': channels,
            'data': data}

        if socket_id:
            params['socket_id'] = validate_socket_id(socket_id)

        return Request(self, POST, "/apps/%s/events" % self.app_id, params)



    @request_method
    def trigger_batch(self, batch=[], already_encoded=False):
        """Trigger multiple events with a single HTTP call.

        http://pusher.com/docs/rest_api#method-post-batch-events
        """
        if not already_encoded:
            for event in batch:

                validate_channel(event['channel'])

                event_name = ensure_text(event['name'], "event_name")
                if len(event['name']) > self.max_len_event_name:
                    raise ValueError("event_name too long")

                event['data'] = data_to_string(event['data'], self._json_encoder)

                if len(event['data']) > self.max_len_data:
                    raise ValueError("Too much data")

                if is_encrypted_channel(event['channel']):
                    event['data'] = json.dumps(encrypt(event['channel'], event['data'], self._encryption_master_key), ensure_ascii=False)

        params = {
            'batch': batch}

        return Request(
            self, POST, "/apps/%s/batch_events" % self.app_id, params)


    @request_method
    def channels_info(self, prefix_filter=None, attributes=[]):
        """Get information on multiple channels, see:

        http://pusher.com/docs/rest_api#method-get-channels
        """
        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)

        if prefix_filter:
            params['filter_by_prefix'] = ensure_text(
                prefix_filter, "prefix_filter")

        return Request(
            self, GET, six.text_type("/apps/%s/channels") % self.app_id, params)


    @request_method
    def channel_info(self, channel, attributes=[]):
        """Get information on a specific channel, see:

        http://pusher.com/docs/rest_api#method-get-channel
        """
        validate_channel(channel)

        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)

        return Request(
            self, GET, "/apps/%s/channels/%s" % (self.app_id, channel), params)


    @request_method
    def users_info(self, channel):
        """Fetch user ids currently subscribed to a presence channel

        http://pusher.com/docs/rest_api#method-get-users
        """
        validate_channel(channel)

        return Request(
            self, GET, "/apps/%s/channels/%s/users" % (self.app_id, channel))
