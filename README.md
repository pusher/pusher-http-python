Pusher Python module
====================

Installation
------------

This module has been tested with Python 2.5 and 2.6.

You can install this module using your package management method or choice, normally `easy_install` or `pip`. For example:

    pip install pusher

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


You can also specify `socket_id` as a separate argument, as described in <http://pusherapp.com/docs/duplicates>:

    p['a_channel'].trigger('an_event', {'some': 'data'}, socket_id)

Advanced usage
--------------

Credentials can also be set in a per-instance basis:

    p = pusher.Pusher(app_id='your-pusher-app-id', key='your-pusher-key', secret='your-pusher-secret')


Google AppEngine
----------------

To force the module to use AppEngine's urlfetch, do the following on setup:

    pusher.channel_type = pusher.GoogleAppEngineChannel

I haven't been able to test this though. Can somebody confirm it works? Thanks! `:-)`


Special thanks
--------------

Special thanks go to [Steve Winton](http://www.nixonmcinnes.co.uk/people/steve/), who implemented a Pusher module in Python for the first time, with focus on AppEngine. This module borrows from his contribution at <http://github.com/swinton/gae-pusherapp>

Copyright
---------

Copyright (c) 2010 New Bamboo. See LICENSE for details.