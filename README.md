# Pusher Python module

## Installation

This module has been tested with Python 2.7.

You can install this module using your package management method of choice, normally `easy_install` or `pip`. For example:

    pip install pusher

## Getting started

After registering at <http://pusherapp.com>, create an instance with your security credentials:

    import pusher
    p = pusher.Pusher(app_id='your-pusher-app-id', key='your-pusher-key', secret='your-pusher-secret')

Trigger an event. Channel names may only contain alphanumeric characters + `_-=@,.;`, and event names may only contain alphanumeric characters + `-_`:

    p['a_channel'].trigger('an_event', {'some': 'data'})


You can also specify `socket_id` as a separate argument, as described in <http://pusherapp.com/docs/duplicates>:

    p['a_channel'].trigger('an_event', {'some': 'data'}, socket_id)

## Custom JSON serialization

If you need custom JSON serialization for handling dates or custom data types, provide a `dumps` function for the pusher instance in addition to credentials as specified above.

You can use a custom encoder class:

    from functools import partial
    p = pusher.Pusher(json_dumps=partial(json.dumps, cls=json.JSONEncoder)))

Or a default encode method named `default_encode_func`:

    from functools import partial
    p = pusher.Pusher(json_dumps=partial(json.dumps, default=default_encode_func))

## Heroku

If you're using Pusher as a Heroku add-on, you can get the config information from the environment variable `PUSHER_URL` of the format `http://key:secret@host/app_id`.

    p = pusher.pusher_from_url()

## Additional channels

Additional channel types are provided in the ext module

## Tornado

To use the Tornado web server to trigger events, use the TornadoChannel as channel_factory (in addition to credentials as mentioned above):

    p = pusher.Pusher(channel_factory = pusher.ext.tornado.TornadoChannel)

To see this functionality in action, look at `examples/tornado_channel.py`.

## Google AppEngine

To force the module to use AppEngine's urlfetch, do the following on setup:

    p = pusher.Pusher(channel_factory = pusher.ext.gae.GoogleAppEngineChannel)

The App Engine Channel also provides async methods that return a future, `trigger_async` and `send_request_async`.

## Running the tests

The `pusher/tests` directory contains the following test files:

* test.py
* acceptance_test.py

The tests can be run using [nose](http://readthedocs.org/docs/nose/en/latest/). You will need to run them individually using `nosetests <filename>` e.g `nosetests acceptance_test.py`
  
The tests defined in `acceptance_test.py` execute against the Pusher service. For these to run you must rename the `test_config.example.py` file to `test_config.py` and update the values in it to valid Pusher application credential files.

## Special thanks

Special thanks go to [Steve Winton](http://www.nixonmcinnes.co.uk/people/steve/), who implemented a Pusher module in Python for the first time, with focus on AppEngine. This module borrows from his contribution at <http://github.com/swinton/gae-pusherapp>

## Copyright

Copyright (c) 2012 Pusher Ltd. See LICENSE for details.
