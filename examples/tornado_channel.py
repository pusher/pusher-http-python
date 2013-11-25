# A tiny script that demonstrates TornadoChannel usage.
#
#  * Fill in your Pusher app id, key and secret.
#  * Get Tornado (you can use virtualenv and pip).
#
#  $ cd pusher_client_python/examples
#  $ python tornado_channel.py
#
#  * Visit http://localhost:8888 in your browser.

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pusher

import tornado.ioloop
import tornado.web

pusher.app_id = 'app_id'
pusher.key = 'key'
pusher.secret = 'secret'

pusher.channel_type = pusher.TornadoChannel

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        def callback(response):
            print "Callback run. Response: %s" % repr(response)

        p = pusher.Pusher()
        # You can receive this event on the app keys page.
        p['test_channel'].trigger('my_event', {'message': 'Hello from tornado'}, callback=callback)

        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    print "Started, visit http://localhost:8888 in your browser to trigger an event"
    tornado.ioloop.IOLoop.instance().start()
