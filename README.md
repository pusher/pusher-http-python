Pusher gem
==========

Getting started
---------------

After registering at <http://pusherapp.com>, configure your app with the security credentials:

    pusher.app_id = 'your-pusher-app-id'
    pusher.key = 'your-pusher-key'
    pusher.secret = 'your-pusher-secret'

Then create an instance:

    p = pusher.Pusher()

Trigger an event. Channel and event names may only contain alphanumeric characters, '-' and '_':

    p['a_channel'].trigger('an_event', {'some': 'data'})


Advanced usage
--------------

Credentials can also be set in a per-instance basis:

    p = pusher.Pusher(app_id='your-pusher-app-id', key='your-pusher-key', secret='your-pusher-secret')

TODO
----

* Google AppEngine support
* Specify `socket_id`

Copyright
---------

Copyright (c) 2010 New Bamboo. See LICENSE for details.