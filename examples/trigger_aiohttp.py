import pusher
import pusher.aiohttp
import asyncio

def main():
    pusher_client = pusher.Pusher.from_env(
            backend=pusher.aiohttp.AsyncIOBackend,
            timeout=50
            )
    print("before trigger")
    response = yield from pusher_client.trigger("hello", "world", dict(foo='bar'))
    print(response)

asyncio.get_event_loop().run_until_complete(main())
