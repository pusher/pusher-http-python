Pusher REST Python library
==========================

![Travis-CI](https://travis-ci.org/pusher/pusher-rest-python.svg)

*status: Alpha*

This is the new python library that will replace the "pusher" module once it
becomes stable enough.

In order to use this library, you need to have an account on
http://pusher.com. After registering, you will need the application
credentials for your app.

Features
--------

* Python 2.6, 2.7 and 3.3 support
* Adapters for various http libraries like requests, aiohttp and tornado
* WebHook validation
* Signature generation for socket subscriptions

Installation
------------

You can install this module using your package management method or choice,
normally `easy_install` or `pip`. For example:

```bash
pip install pusher-rest
```

Getting started
---------------

The minimum configuration required to use the Pusher object are the three
constructor arguments which identify your Pusher app. You can find them by
going to "API Keys" on your app at https://app.pusher.com.

```python
from pusher import Config, Pusher
pusher = Pusher(config=Config(app_id=u'4', key=u'key', secret=u'secret'))
```

You can then trigger events to channels. Channel and event names may only
contain alphanumeric characters, `-` and `_`:

```python
pusher.trigger('a_channel', 'an_event', {'some': 'data'})
```

You can also specify `socket_id` as a separate argument, as described in
<http://pusher.com/docs/duplicates>:

```python
pusher.trigger('a_channel', 'an_event', {'some': 'data'}, socket_id)
```

### Additional options

The Config and Pusher constructors supports more options. See the code
documentation to get all the details.

TODO: Add link to code docs here

Running the tests
-----------------

To run the tests run `python setup.py test`

License
-------

Copyright (c) 2014 Pusher Ltd. See LICENSE for details.

