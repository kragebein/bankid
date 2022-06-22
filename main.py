#!/usr/bin/python3.10
import asyncio
from bankid.webserver import Webserver
import bankid.warden

log = bankid.warden.Warden()
log.loglevel = bankid.warden.DEBUG
log.application_name = 'bidi'


if __name__ == '__main__':
    web = Webserver()
    try:
        asyncio.run(web.run())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(web.run())
