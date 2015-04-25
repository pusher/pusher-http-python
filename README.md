# Pusher HTTP Python Library

![Travis-CI](https://travis-ci.org/pusher/pusher-http-python.svg)

*status: Alpha*

The new Python library for interacting with the Pusher HTTP API.

This package lets you trigger events to your client and query the state of your Pusher channels. When used with a server, you can validate Pusher webhooks and authenticate private- or presence-channels.

In order to use this library, you need to have a free account on <http://pusher.com>. After registering, you will need the application credentials for your app.

Features
--------

* Python 2.6, 2.7 and 3.3 support
* Adapters for various http libraries like requests, urlfetch, aiohttp and tornado.
* WebHook validation
* Signature generation for socket subscriptions

###Table of Contents

- [Installation](#installation)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Triggering Events](#triggering-events)
- [Querying Application State](#querying-application-state)
  - [Getting Information For All Channels](#getting-information-for-all-channels)
  - [Getting Information For A Specific Channel](#getting-information-for-a-specific-channel)
  - [Getting User Information For A Presence Channel](#getting-user-information-for-a-presence-channel)
- [Authenticating Channel Subscription](#authenticating-channel-subscription)
- [Receiving Webhooks](#receiving-webhooks)
- [Request Library Configuration](#request-library-configuration)
  - [Google App Engine](#google-app-engine)
- [Feature Support](#feature-support)
- [Running the tests](#running-the-tests)
- [License](#license)

Installation
------------

You can install this module using your package management method or choice,
normally `easy_install` or `pip`. For example:

```bash
pip install pusher
```

**Note: When 1.0 is reached `pusher-rest` will no longer be updated. Instead `pusher` should be used**

Getting started
---------------

The minimum configuration required to use the Pusher object are the three
constructor arguments which identify your Pusher app. You can find them by
going to "API Keys" on your app at <https://app.pusher.com>.

```python
from pusher import Pusher
pusher = Pusher(app_id=u'4', key=u'key', secret=u'secret')
```

You can then trigger events to channels. Channel and event names may only
contain alphanumeric characters, `-` and `_`:

```python
pusher.trigger(u'a_channel', u'an_event', {u'some': u'data'})
```

## Configuration

```python
from pusher import Pusher
pusher = Pusher(app_id, key, secret)
```

|Argument   |Description   |
|:-:|:-:|
|app_id `String`  |**Required** <br> The Pusher application ID |
|key `String`     |**Required** <br> The Pusher application key |
|secret `String`  |**Required** <br> The Pusher application secret token |
|host `String`    | **Default:`None`** <br> The host to connect to |
|port `int`       | **Default:`None`** <br>Which port to connect to |
|ssl `bool`       | **Default:`True`** <br> Use HTTPS |
|cluster `String` | **Default:`None`** <br> Convention for other clusters than the main Pusher-one. Eg: 'eu' will resolve to the api-eu.pusherapp.com host |
|backend `Object` | an object that responds to the send_request(request) method. If none is provided, a `pusher.requests.RequestsBackend` instance is created. |

##### Example

```py
from pusher import Pusher
pusher = Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'eu')
```

Triggering Events
-----------------

To trigger an event on one or more channels, use the `trigger` method on the `Pusher` object.

#### `Pusher::trigger`

|Argument   |Description   |
|:-:|:-:|
|channels `String` or `Collection`   |**Required** <br> The name or list of names of the channel you wish to trigger events on   |
|event `String`| **Required** <br> The name of the event you wish to trigger. |
|data `JSONable data` | **Required** <br> The event's payload |
|socket_id `String` | **Default:`None`** <br> The socket_id of the connection you wish to exclude from receiving the event. You can read more [here](http://pusher.com/docs/duplicates). |

|Return Values   |Description   |
|:-:|:-:|
|buffered_events `Dict`   | A parsed response that includes the event_id for each event published to a channel. See example.   |

##### Example

This call will trigger to `'a_channel'` and `'another_channel'`, and exclude the recipient with socket_id `"1234.12"`.

```python
pusher.trigger([u'a_channel', u'another_channel'], u'an_event', {u'some': u'data'}, "1234.12")
```

#### Event Buffer

Version 1.0.0 of the library introduced support for event buffering. The purpose of this functionality is to ensure that events that are triggered during whilst a client is offline for a short period of time will still be delivered upon reconnection.

Note: this requires your Pusher application to be on a cluster that has the Event Buffer capability.

As part of this the trigger function now returns a set of event_id values for each event triggered on a channel. These can then be used by the client to tell the Pusher service the last event it has received. If additional events have been triggered after that event ID the service has the opportunity to provide the client with those IDs.

##### Example

```python
events = pusher.trigger([u'a_channel', u'another_channel'], u'an_event', {u'some': u'data'}, "1234.12")

#=> {'event_ids': {'another_channel': 'eudhq17zrhfbwc', 'a_channel': 'eudhq17zrhfbtn'}}
```

Querying Application State
-----------------

### Getting Information For All Channels


#### `Pusher::channels_info`

|Argument   |Description |
|:-:|:-:|
|prefix_filter `String`  |**Default: `None`** <br> Filter the channels returned by their prefix   |
|attributes `Collection` | **Default: `[]`** <br> A collection of attributes which should be returned for each channel. If empty, an empty dictionary of attributes will be returned for each channel. <br> Available attributes: `"user_count"`.

|Return Values   |Description   |
|:-:|:-:|
|channels `Dict`   | A parsed response from the HTTP API. See example.   |

##### Example

```python
channels = pusher.channels_info(u"presence-", [u'user_count'])

#=> {u'channels': {u'presence-chatroom': {u'user_count': 2}, u'presence-notifications': {u'user_count': 1}}}
```

### Getting Information For A Specific Channel

#### `Pusher::channel_info`

|Argument   |Description   |
|:-:|:-:|
|channel `String`  |**Required** <br> The name of the channel you wish to query|
|attributes `Collection` | **Default: `[]`** <br> A collection of attributes to be returned for the channel. <br><br> Available attributes: <br> `"user_count"` : Number of *distinct* users currently subscribed. **Applicable only to presence channels**. <br> `"subscription_count"`: [BETA]: Number of *connections* currently subscribed to the channel. Please [contact us](http://support.pusher.com) to enable this feature.

|Return Values   |Description   |
|:-:|:-:|
|channel `Dict`   |  A parsed response from the HTTP API. See example.  |

##### Example

```python
channel = pusher.channel_info(u'presence-chatroom', [u"user_count"])
#=> {u'user_count': 42, u'occupied': True}
```

### Getting User Information For A Presence Channel

#### `Pusher::users_info`

|Argument   |Description   |
|:-:|:-:|
|channel `String`   |**Required** <br> The name of the *presence* channel you wish to query   |

|Return Values   |Description   |
|:-:|:-:|
|users `Dict`   | A parsed response from the HTTP API. See example.   |

##### Example

```python
pusher.users_info(u'presence-chatroom')
#=> {u'users': [{u'id': u'1035'}, {u'id': u'4821'}]}
```

Authenticating Channel Subscription
-----------------

#### `Pusher::authenticate`

In order for users to subscribe to a private- or presence-channel, they must be authenticated by your server.

The client will make a POST request to an endpoint (either "/pusher/auth" or any which you specify) with a body consisting of the channel's name and socket_id.

Using your `Pusher` instance, with which you initialized `Pusher`, you can generate an authentication signature. Having responded to the request with this signature, the subscription will be authenticated.

|Argument   |Description   |
|:-:|:-:|
|channel `String`   |**Required**<br> The name of the channel, sent to you in the POST request    |
|socket_id `String` | **Required**<br> The channel's socket_id, also sent to you in the POST request |
|custom_data `Dict` |**Required for presence channels** <br> This will be a dictionary containing the data you want associated with a member of a presence channel. A `"user_id"` key is *required*, and you can optionally pass in a `"user_info"` key. See the example below.  |

|Return Values   |Description   |
|:-:|:-:|
|response `Dict`   | A dictionary to send as a response to the authentication request.|

##### Example

###### Private Channels

```python
auth = pusher.authenticate_subscription(

  channel=u"private-channel",

  socket_id=u"1234.12"
)
# return `auth` as a response
```

###### Presence Channels

```python
auth = pusher.authenticate_subscription(

  channel=u"presence-channel",

  socket_id=u"1234.12",

  custom_data={
    u'user_id': u'1',
    u'user_info': {
      u'twitter': '@pusher'
    }
  }
)
# return `auth` as a response
```

Receiving Webhooks
-----------------

If you have webhooks set up to POST a payload to a specified endpoint, you may wish to validate that these are actually from Pusher. The `Pusher` object achieves this by checking the authentication signature in the request body using your application credentials.

#### `Pusher::validate_webhook`

|Argument   |Description   |
|:-:|:-:|
|key `String`   | **Required**<br>Pass in the value sent in the request headers under the key "X-PUSHER-KEY". The method will check this matches your app key.   |
|signature `String` | **Required**<br>This is the value in the request headers under the key "X-PUSHER-SIGNATURE". The method will verify that this is the result of signing the request body against your app secret.  |
|body `String` | **Required**<br>The JSON string of the request body received. |

|Return Values   |Description   |
|:-:|:-:|
|body_data `Dict`   | If validation was successful, the return value will be the parsed payload. Otherwise, it will be `None`.   |

##### Example

```python
webhook = pusher.validate_webhook(

  key="key_sent_in_header",

  signature="signature_sent_in_header",

  body="{ \"time_ms\": 1327078148132  \"events\": [ { \"name\": \"event_name\", \"some\": \"data\" }  ]}"
)

print webhook["events"]
```

## Request Library Configuration

Users can configure the library to use different backends to send calls to our API. The HTTP libraries we support are:

* [Requests](http://docs.python-requests.org/en/latest/) (`pusher.requests.RequestsBackend`). This is used by default. 
* [Tornado](http://www.tornadoweb.org/en/stable/) (`pusher.tornado.TornadoBackend`).
* [AsyncIO](http://asyncio.org/) (`pusher.aiohttp.AsyncIOBackend`).
* [URLFetch](https://pypi.python.org/pypi/urlfetch) (`pusher.urlfetch.URLFetchBackend`).

Upon initializing a Pusher instance, pass in any of these options to the `backend` keyword argument. 

### Google App Engine

GAE users are advised to use the URLFetch backend to ensure compatability.

## Feature Support

Feature                                    | Supported
-------------------------------------------| :-------:
Trigger event on single channel            | *&#10004;*
Trigger event on multiple channels         | *&#10004;*
Excluding recipients from events           | *&#10004;*
Authenticating private channels            | *&#10004;*
Authenticating presence channels           | *&#10004;*
Get the list of channels in an application | *&#10004;*
Get the state of a single channel          | *&#10004;*
Get a list of users in a presence channel  | *&#10004;*
WebHook validation                         | *&#10004;*
Heroku add-on support						   | *&#10004;*
Debugging & Logging                        | *&#10004;*
Cluster configuration                      | *&#10004;*
Timeouts                                   | *&#10004;*
HTTPS                                      | *&#10004;*
HTTP Proxy configuration                   | *&#10008;*
HTTP KeepAlive                             | *&#10008;*

#### Helper Functionality

These are helpers that have been implemented to to ensure interactions with the HTTP API only occur if they will not be rejected e.g. [channel naming conventions](https://pusher.com/docs/client_api_guide/client_channels#naming-channels).

Helper Functionality                     | Supported
-----------------------------------------| :-------:
Channel name validation 					 | &#10004;
Limit to 10 channels per trigger         | &#10004;
Limit event name length to 200 chars     | &#10004;


Running the tests
-----------------

To run the tests run `python setup.py test`

License
-------

Copyright (c) 2015 Pusher Ltd. See LICENSE for details.
