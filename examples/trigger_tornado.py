import pusher
import pusher.tornado
import tornado.ioloop

ioloop = tornado.ioloop.IOLoop.instance()

def show_response(response):
    print(response.result())
    ioloop.stop()

pusher_client = pusher.Pusher.from_env(
            backend=pusher.tornado.TornadoBackend,
            timeout=50
         )
response = pusher_client.trigger("hello", "world", dict(foo='bar'))
response.add_done_callback(show_response)
print("Before start")
ioloop.start()
print("After start")
