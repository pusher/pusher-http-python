import pusher
import pusher.aiohttp
import asyncio

def main():
    client = pusher.Pusher.from_env(
            backend=pusher.aiohttp.AsyncIOBackend,
            timeout=50
            )
    print("before trigger")
    response = yield from client.trigger("hello", "world", dict(foo='bar'))
    print(response)

asyncio.get_event_loop().run_until_complete(main())
