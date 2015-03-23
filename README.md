# Pusher Python module

**Version 1.0 of this module is under development in the [1.0.0 branch](https://github.com/pusher/pusher-http-python/tree/1.0.0)**

## Installation

This module has been tested with Python 2.6 and 2.7.

You can install this module using your package management method or choice, normally `easy_install` or `pip`. For example:

    pip install pusher

## Getting started

After registering at <http://pusherapp.com>, create an instance, specifying your security credentials:

    p = pusher.Pusher(app_id='your-pusher-app-id', key='your-pusher-key', secret='your-pusher-secret')

You can then create channels and trigger events. Channel and event names may only contain alphanumeric characters, '-' and '_':

    p['a_channel'].trigger('an_event', {'some': 'data'})


You can also specify `socket_id` as a separate argument, as described in <http://pusherapp.com/docs/duplicates>:

    p['a_channel'].trigger('an_event', {'some': 'data'}, socket_id)

## Advanced usage

A custom json encoder class, such as the one provided by Django may also be specified:

    from django.core.serializers.json import DjangoJSONEncoder
    p = pusher.Pusher(app_id=..., encoder=DjangoJSONEncoder)

## Heroku

If you're using Pusher as a Heroku add-on, you can just get the config information like this:

    p = pusher.pusher_from_url()

## Tornado

To use the Tornado web server to trigger events, set `channel_type`:

    pusher.channel_type = pusher.TornadoChannel

To see this functionality in action, look at `examples/tornado_channel.py`.

## Google AppEngine

To force the module to use AppEngine's urlfetch, do the following on setup:

    pusher.channel_type = pusher.GoogleAppEngineChannel

## Google AppEngine NDB

A channel that uses the GAE NDB (introduced in GAE 1.6.3) and provides async methods that return a future, `trigger_async` and `send_request_async`.

    pusher.channel_type = pusher.GaeNdbChannel

## Running the tests

The `pusher` directory contains the following test files:

* test.py
* acceptance_test.py

The tests can be run using [nose](http://readthedocs.org/docs/nose/en/latest/). You will need to run them individually using `nosetests <filename>` e.g `nosetests acceptance_test.py`
  
The tests defined in `acceptance_test.py` execute against the Pusher service. For these to run you must rename the `test_config.example.py` file to `test_config.py` and update the values in it to valid Pusher application credential files.

## Special thanks

Special thanks go to [Steve Winton](http://www.nixonmcinnes.co.uk/people/steve/), who implemented a Pusher module in Python for the first time, with focus on AppEngine. This module borrows from his contribution at <http://github.com/swinton/gae-pusherapp>

## Copyright

Copyright (c) 2012 Pusher Ltd. See LICENSE for details.
