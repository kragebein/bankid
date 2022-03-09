import aiohttp_jinja2
import asyncio
import jinja2
import json
import traceback
import hashlib
import datetime

from aiohttp import web
from bankid.config import Config
from bankid.bankid import BankID
from bankid.classes import Auth, Api
from bankid.stats import Stats
from bankid.db import Database


class Webserver():

    host: str = None
    port: str = None

    def __init__(self):
        self.db = Database()
        self.stat = Stats(self.db)
        self.bidi = BankID(self.db)
        self.config = Config()

    async def run(self) -> None:
        ''' Sets up and runs an aiohttp web server with the bankid and api routes
        THIS IS BLOCKING
        '''
        app = web.Application()

        aiohttp_jinja2.setup(
            app,
            loader=jinja2.FileSystemLoader('templates'))

        app.add_routes(
            [
             web.get('/{key}/bankid', self.bankid),
             web.get('/{key}/api', self.api),
             web.post('/{key}/admin', self.get_stats_post),
             web.get('/{key}/admin', self.get_stats)
                ]
            )

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()
        await asyncio.Event().wait()

    async def auth(self, key):
        ''' Creats an Auth Object with information about caller '''
        a = Auth(key, self.db)

        # If the authorization key is okay, the
        # Auth object will contain the details of the caller.
        return a

    async def get_stats_post(self, request):
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:
            await self.stat.authorized()
            data = await request.post()
            add_data = {data[x] for x in data}
            required = ['api', 'email', 'name', 'phone', 'payment_method', 'expiry_timer']
            for key in add_data:
                if len(add_data[key]) == 0:
                    return await self.get_stats(request, indata='Not completed properly')

        return await self.unauthorized()

    async def get_stats(self, request, indata=None) -> web.Response:
        ''' Api View of different statistics from the database.'''
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:
            await self.stat.authorized()
            try:
                if 'Stian Langvann' in auth.user:
                    stat, hits, success, fails, errors = await self.stat.get_stats()
                    new_key = str(datetime.datetime.now())
                    key = hashlib.md5(new_key.encode())

                    data = {
                        'total_hits': hits,
                        'total_success': success,
                        'total_failed': fails,
                        'errors': errors,
                        'new_key': key.hexdigest()
                    }

                    return aiohttp_jinja2.render_template(
                        'admin.html',
                        request,
                        data
                    )

            except Exception:
                traceback.print_exc()
                return await self.unauthorized()
        return await self.unauthorized()

    async def api(self, request) -> web.Response:
        ''' Handles the "api" endpoint, checks with auth and returns an Api Object in dict form.'''
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:

            await self.stat.authorized()

            # Build the Api endpoint
            await self.bidi.update()
            response = Api(
                    {'auth': 'Authorized'},
                    self.bidi.api,
                    self.bidi.openapi
                    ).__dict__

            # Returns the Api endpoint
            return web.Response(
                content_type="application/json",
                text=str(json.dumps(response, indent=2)),
                status=200
                )

        # or return the unauthorized message
        return await self.unauthorized()

    async def bankid(self, request):
        ''' Handles the "bankid" endpoint. Returns a jinja html template.'''
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:
            await self.stat.authorized()

            # Returns the Jinja Document
            await self.bidi.update()
            data = self.bidi.get_status()
            return_data = aiohttp_jinja2.render_template(
                'bankid.html',
                request,
                data.__dict__,
                status=200
                )
            return return_data
        # or returns the unauthorized message
        return await self.unauthorized()

    async def unauthorized(self):
        message = {'message': {'auth': 'Unauthorized'}}

        await self.stat.unauthorized()

        return web.Response(
            content_type="application/json",
            text=json.dumps(message, indent=2),
            status=403
            )
