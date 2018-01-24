### 1.7.3 2018-01-24

* Replace `read_and_close` with `text` in aiohttp adaptor (method removed
  upstream)

### 1.7.2 2017-07-19

* Remove `webhook_level` option to notify (depricated upstream)

* Increase notify timeout to 30s

### 1.7.1 2017-06-12

* Make python 2 and 3 support explicit in `setup.py`

* Lift trigger channel limit to 100 for consistency with API

### 1.7.0 2017-05-12

* Remove version freeze from urllib3 since upstream bugfix has been released. (See [here](https://github.com/shazow/urllib3/pull/987).)

### 1.6.0 1016-10-26

* Path to cacert.pem has been added to the setup.py, resolving an oversight that led to errors upon SSL requests.
* Internal changes to ease future maintenance.

### 1.5.0 2016-08-23

* Add support for publishing push notifications on up to 10 interests.

### 1.4.0 2016-08-15

* Add support for sending push notifications.

### 1.3.0 2016-05-24

* Add support for batch events

### 1.2.3 2015-06-22

* Fixes sharing default mutable argument between requests
* Only load RequestsBackend when required (avoids issues on GAE)

### 1.2.2 2015-06-12

Added Wheel file publishing. No functional changes.

### 1.2.1 2015-06-03

Added cacert.pem to the package, getting rid of errors upon SSL calls.

### 1.2.0 2015-05-29

* Renamed `URLFetchBackend` to `GAEBackend`, which specifically imports the Google App Engine urlfetch library.
* Library creates an SSL context from certificate, addressing users receiving `InsecurePlatformWarning`s.

### 1.1.3 2015-05-12

Tightened up socket_id validation regex.

### 1.1.2 2015-05-08

Fixed oversight in socket_id validation regex.

### 1.1.1 2015-05-08

* Library now validates `socket_id` for the `trigger` method.

### 1.1.0 2015-05-07

* User can now specify a custom JSON encoder or decoder upon initializing Pusher.

### 1.0.0 2015-04-25

* Python 2.6, 2.7 and 3.3 support
* Adapters for various http libraries like requests, urlfetch, aiohttp and tornado.
* WebHook validation
* Signature generation for socket subscriptions

### 0.1.0 2014-09-01

* First release
