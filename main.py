#!/usr/bin/python3.10
import asyncio
from bankid.webserver import Webserver
import bankid.warden

log = bankid.warden.Warden()
log.application_name = 'bidi'
log.loglevel = bankid.warden.DEBUG

if __name__ == '__main__':
    web = Webserver()
    try:
        asyncio.run(web.run())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(web.run())
