import aiohttp_jinja2
import asyncio
import jinja2
import json

from aiohttp import web
from bankid.config import Config
from bankid.bankid import BankID
from bankid.classes import Auth, Api
from bankid.stats import Stats


class Webserver():

    host: str = None
    port: str = None

    def __init__(self):

        self.stat = Stats()
        self.bidi = BankID(self.stat)
        self.config = Config()

    async def run(self) -> None:
        ''' Sets up and runs an aiohttp web server with the bankid and api routes'''
        app = web.Application()

        aiohttp_jinja2.setup(
            app,
            loader=jinja2.FileSystemLoader('templates'))

        app.add_routes(
            [
             web.get('/{key}/bankid', self.handler),
             web.get('/{key}/api', self.api),
             web.get('/{key}/stats', self.get_stats)
                ]
            )

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()
        await asyncio.Event().wait()

    async def auth(self, key):
        ''' Creats an Auth Object with information about caller '''
        a = Auth(key)

        # If the authorization key is okay, the
        # Auth object will contain the details of the caller.
        return a

    async def get_stats(self, request) -> web.Response:
        ''' Api View of different statistics from the database.'''
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:

            if 'Stian Langvann' in auth.user:
                stat, hits, success, fails, errors = await self.stat.get_stats()
                data = {
                    'total_hits': hits,
                    'total_success': success,
                    'total_failed': fails,
                    'errors': errors
                }
                return web.Response(
                    text=json.dumps(data, indent=2)
                )
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

    async def handler(self, request):
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
