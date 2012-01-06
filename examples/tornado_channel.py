# A tiny script that demonstrates TornadoChannel usage.
#
#  * Fill in your Pusher app id, key and secret.
#  * Get Tornado (you can use virtualenv and pip).
#
#  $ cd pusher_client_python/examples
#  $ python tornado_channel.py
#
#  * Visit http://localhost:8888 in your browser.

import sys
sys.path.append("../")

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
            print "Callback run."

        p = pusher.Pusher()
        p['a_channel'].trigger('an_event', {'some': 'data'}, callback=callback)

        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
