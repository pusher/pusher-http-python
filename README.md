Pusher REST Python library
==========================

*status: Alpha*

This is the new python library that will replace the "pusher" module once it
becomes stable enough.

In order to use this library, you need to have an account on
http://pusher.com. After registering, you will need the application
credentials for your app.

Features
--------

* Python 2 and 3 support
* Adapters for various http libraries like requests, aiohttp and tornado
* WebHook validation
* Signature generation for socket subscriptions

Installation
------------

The pusher-rest-python library will be availabe on PyPi:
`pip install python-rest`

Configuration
-------------

The minimum configuration required to use the Pusher object are the three
constructor arguments which identify your Pusher app. You can find them by
going to "API Keys" on your app at https://app.pusher.com.

```python
from pusher import Config, Pusher
pusher = Pusher(config=Config(app_id=u'4', key=u'key', secret=u'secret'))
```

### From URL

```python
from pusher import Config, Pusher
pusher = Pusher(config=Config.from_url(u'http://key:secret@somehost/apps/4'))
```

### From ENV

On Heroku the addon sets the PUSHER_URL environment variable with the url.

```python
from pusher import Config, Pusher
pusher = Pusher(config=Config.from_env())
```

### Additional options

The Config and Pusher constructors supports more options. See the code
documentation to get all the details.

TODO: Add link to code docs here

Test
----

To run the tests run `python setup.py test`

License
-------

This code is free to use under the terms of the MIT license.

