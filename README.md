# Pusher Channels HTTP Python Library

[![Build Status](https://travis-ci.org/pusher/pusher-http-python.svg?branch=master)](https://travis-ci.org/pusher/pusher-http-python)

This package lets you trigger events to your client and query the state of your channels. When used with a server, you can validate webhooks and authenticate `private-` or `presence-` channels.

In order to use this library, you need to have a free account on <http://pusher.com>. After registering, you will need the application credentials for your app.

## Supported Platforms

* Python - supports Python versions 2.7, 3.6, 3.7 and 3.8

## Features

* Adapters for various http libraries like requests, urlfetch, aiohttp (requires Python >= 3.5.3) and tornado.
* WebHook validation
* Signature generation for socket subscriptions

### Table of Contents

- [Installation](#installation)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Triggering Events](#triggering-events)
- [Querying Application State](#querying-application-state)
  - [Getting Information For All Channels](#getting-information-for-all-channels)
  - [Getting Information For A Specific Channel](#getting-information-for-a-specific-channel)
  - [Getting User Information For A Presence Channel](#getting-user-information-for-a-presence-channel)
- [Authenticating Channel Subscription](#authenticating-channel-subscription)
- [End-to-end Encryption](#end-to-end-encryption)
- [Receiving Webhooks](#receiving-webhooks)
- [Request Library Configuration](#request-library-configuration)
  - [Google App Engine](#google-app-engine)
- [Feature Support](#feature-support)
- [Running the tests](#running-the-tests)
- [License](#license)

## Installation

You can install this module using your package management method or choice,
normally `easy_install` or `pip`. For example:

```bash
pip install pusher
```

Users on Python 2.x and older versions of pip may get a warning, due to pip compiling the optional `pusher.aiohttp` module, which uses Python 3 syntax. However, as `pusher.aiohttp` is not used by default, this does not affect the library's functionality. See [our Github issue](https://github.com/pusher/pusher-http-python/issues/52), as well as [this issue from Gunicorn](https://github.com/benoitc/gunicorn/issues/788) for more details.

On Linux, you must ensure that OpenSSL is installed, e.g. on Debian/Ubuntu:

```sh
$ sudo apt-get install build-essential libssl-dev libffi-dev
```

## Getting started

 The minimum configuration required to use the `Pusher` object are the three
constructor arguments which identify your Pusher Channels app. You can find them by
going to "API Keys" on your app at <https://app.pusher.com>.

```python
import pusher
pusher_client = pusher.Pusher(app_id=u'4', key=u'key', secret=u'secret', cluster=u'cluster')
```

You can then trigger events to channels. Channel and event names may only
contain alphanumeric characters, `-` and `_`:

```python
pusher_client.trigger(u'a_channel', u'an_event', {u'some': u'data'})
```

## Configuration

```python
import pusher
pusher_client = pusher.Pusher(app_id, key, secret, cluster=u'cluster')
```

|Argument   |Description   |
|:-:|:-:|
|app_id `String`  |**Required** <br> The Pusher Channels application ID |
|key `String`     |**Required** <br> The Pusher Channels application key |
|secret `String`  |**Required** <br> The Pusher Channels application secret token |
|cluster `String` | **Default:`mt1`** <br> The pusher application cluster. Will be overwritten if `host` is set |
|host `String`    | **Default:`None`** <br> The host to connect to |
|port `int`       | **Default:`None`** <br>Which port to connect to |
|ssl `bool`       | **Default:`True`** <br> Use HTTPS |
|~~encryption_master_key~~ `String` | **Default:`None`** <br> *Deprecated*, see `encryption_master_key_base64` |
|encryption_master_key_base64 `String` | **Default:`None`** <br> The encryption master key for End-to-end Encryption |
|backend `Object` | an object that responds to the `send_request(request)` method. If none is provided, a `pusher.requests.RequestsBackend` instance is created. |
|json_encoder `Object` | **Default: `None`**<br> Custom JSON encoder. |
|json_decoder `Object` | **Default: `None`**<br> Custom JSON decoder.

The constructor will throw a `TypeError` if it is called with parameters that don’t match the types listed above.

##### Example

```py
import pusher
pusher_client = pusher.Pusher(app_id=u'4', key=u'key', secret=u'secret', ssl=True, cluster=u'cluster')
```

## Triggering Events

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

`Pusher::trigger` will throw a `TypeError` if called with parameters of the wrong type; or a `ValueError` if called on more than 100 channels, with an event name longer than 200 characters, or with more than 10240 characters of data (post JSON serialisation).

##### Example

This call will trigger to `'a_channel'` and `'another_channel'`, and exclude the recipient with socket_id `"1234.12"`.

```python
pusher_client.trigger([u'a_channel', u'another_channel'], u'an_event', {u'some': u'data'}, "1234.12")
```

#### `Pusher::trigger_batch`

It's also possible to send distinct messages in batches to limit the overhead
of HTTP headers. There is a current limit of 10 events per batch on
our multi-tenant clusters.

|Argument   |Description   |
|:-:|:-:|
|batch `Array` of `Dict`  |**Required** <br> A list of events to trigger   |

Events are a `Dict` with keys:

|Argument   |Description   |
|:-:|:-:|
|channel `String`| **Required** <br> The name of the channel to publish to. |
|name `String`| **Required** <br> The name of the event you wish to trigger. |
|data `JSONable data` | **Required** <br> The event's payload |
|socket_id `String` | **Default:`None`** <br> The socket_id of the connection you wish to exclude from receiving the event. You can read more [here](http://pusher.com/docs/duplicates). |

|Return Values   |Description   |
|:-:|:-:|
|`Dict`| An empty dict on success |

`Pusher::trigger_batch` will throw a `TypeError` if the data parameter is not JSONable.

##### Example

```python
pusher_client.trigger_batch([
  { u'channel': u'a_channel', u'name': u'an_event', u'data': {u'some': u'data'}, u'socket_id': '1234.12'},
  { u'channel': u'a_channel', u'name': u'an_event', u'data': {u'some': u'other data'}}
])
```

## Querying Application State

### Getting Information For All Channels


#### `Pusher::channels_info`

|Argument   |Description |
|:-:|:-:|
|prefix_filter `String`  |**Default: `None`** <br> Filter the channels returned by their prefix   |
|attributes `Collection` | **Default: `[]`** <br> A collection of attributes which should be returned for each channel. If empty, an empty dictionary of attributes will be returned for each channel. <br> Available attributes: `"user_count"`.

|Return Values   |Description   |
|:-:|:-:|
|channels `Dict`   | A parsed response from the HTTP API. See example.   |

`Pusher::channels_info` will throw a `TypeError` if `prefix_filter` is not a `String`.

##### Example

```python
channels = pusher_client.channels_info(u"presence-", [u'user_count'])

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

`Pusher::channel_info` will throw a `ValueError` if `channel` is not a valid channel.

##### Example

```python
channel = pusher_client.channel_info(u'presence-chatroom', [u"user_count"])
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

`Pusher::users_info` will throw a `ValueError` if `channel` is not a valid channel.

##### Example

```python
pusher_client.users_info(u'presence-chatroom')
#=> {u'users': [{u'id': u'1035'}, {u'id': u'4821'}]}
```

## Authenticating Channel Subscription

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

`Pusher::authenticate` will throw a `ValueError` if the `channel` or `socket_id` that it’s called with are invalid.

##### Example

###### Private Channels

```python
auth = pusher_client.authenticate(

  channel=u"private-channel",

  socket_id=u"1234.12"
)
# return `auth` as a response
```

###### Presence Channels

```python
auth = pusher_client.authenticate(

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

## End to End Encryption

This library supports end to end encryption of your private channels. This
means that only you and your connected clients will be able to read your
messages. Pusher cannot decrypt them. You can enable this feature by following
these steps:

1. You should first set up Private channels. This involves [creating an
   authentication endpoint on your
   server](https://pusher.com/docs/authenticating_users).

2. Next, generate a 32 byte master encryption key, base64 encode it and store
   it securely.

   This is secret and you should never share this with anyone. Not even Pusher.

   To generate a suitable key from a secure random source, you could use:

   ```bash
   openssl rand -base64 32
   ```

3. Pass your master key to the SDK constructor

   ```python
   import pusher

   pusher_client = pusher.Pusher(
     app_id='yourappid',
     key='yourkey',
     secret='yoursecret',
     encryption_master_key_base64='<output from command above>',
     cluster='yourclustername',
     ssl=True
   )

   pusher_client.trigger('private-encrypted-my-channel', 'my-event', {
     'message': 'hello world'
   })
   ```

4. Channels where you wish to use end to end encryption must be prefixed with
   `private-encrypted-`.

5. Subscribe to these channels in your client, and you're done! You can verify
   it is working by checking out the debug console on the
   https://dashboard.pusher.com/ and seeing the scrambled ciphertext.

**Important note: This will not encrypt messages on channels that are not prefixed by private-encrypted-.**

More info on End-to-end Encrypted Channels [here](https://pusher.com/docs/client_api_guide/client_encrypted_channels).

## Receiving Webhooks

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

`Pusher::validate_webhook` will raise a `TypeError` if it is called with any parameters of the wrong type.

##### Example

```python
webhook = pusher_client.validate_webhook(

  key="key_sent_in_header",

  signature="signature_sent_in_header",

  body="{ \"time_ms\": 1327078148132  \"events\": [ { \"name\": \"event_name\", \"some\": \"data\" }  ]}"
)

print webhook["events"]
```

## Request Library Configuration

Users can configure the library to use different backends to send calls to our API. The HTTP libraries we support are:

* [Requests](https://requests.readthedocs.io/en/master/) (`pusher.requests.RequestsBackend`). This is used by default.
* [Tornado](http://www.tornadoweb.org/en/stable/) (`pusher.tornado.TornadoBackend`).
* [AsyncIO](https://docs.python.org/3/library/asyncio.html) (`pusher.aiohttp.AsyncIOBackend`).
* [Google App Engine](https://cloud.google.com/appengine/docs/python/urlfetch/) (`pusher.gae.GAEBackend`).

Upon initializing a `Pusher` instance, pass in any of these options to the `backend` keyword argument.

### Google App Engine

GAE users are advised to use the `pusher.gae.GAEBackend` backend to ensure compatability.

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
Heroku add-on support                      | *&#10004;*
Debugging & Logging                        | *&#10004;*
Cluster configuration                      | *&#10004;*
Timeouts                                   | *&#10004;*
HTTPS                                      | *&#10004;*
End-to-end Encryption                      | *&#10004;*
HTTP Proxy configuration                   | *&#10008;*
HTTP KeepAlive                             | *&#10008;*

#### Helper Functionality

These are helpers that have been implemented to to ensure interactions with the HTTP API only occur if they will not be rejected e.g. [channel naming conventions](https://pusher.com/docs/channels/using_channels/channels#channel-naming-conventions).

Helper Functionality                     | Supported
-----------------------------------------| :-------:
Channel name validation                  | &#10004;
Limit to 100 channels per trigger        | &#10004;
Limit event name length to 200 chars     | &#10004;


## Running the tests

To run the tests run `python setup.py test`

## License

Copyright (c) 2015 Pusher Ltd. See LICENSE for details.
