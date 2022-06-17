#!/usr/bin/python3.10
import asyncio
from bankid.webserver import Webserver


if __name__ == '__main__':
    web = Webserver()
    try:
        asyncio.run(web.run())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(web.run())
