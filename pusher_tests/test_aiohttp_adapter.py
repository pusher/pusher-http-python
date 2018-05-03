import sys

if sys.version_info >= (3,5,3):
    from .aio.aiohttp_adapter_test import *
