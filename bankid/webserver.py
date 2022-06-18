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
from bankid.stats import Stats, Timeline
from bankid.db import Database
from bankid.slack import Slack


class Webserver:

    host: str = None
    port: str = None

    def __init__(self):
        self.db = Database()
        self.stat = Stats(self.db)
        self.bidi = BankID(self.stat)
        self.config = Config()
        self.slack = Slack(self.db)
        self.timeline = Timeline()

    async def run(self) -> None:
        '''Sets up and runs an aiohttp web server with the bankid and api routes
        THIS IS BLOCKING
        '''
        self.config.read(self)
        app = web.Application()
        loop = asyncio.get_event_loop()
        loop.create_task(self.bidi.updateloop())
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

        app.add_routes(
            [
                web.get('/{key}/bankid', self.bankid),
                web.get('/{key}/api', self.api),
                web.post('/{key}/admin', self.get_stats_post),
                web.get('/{key}/admin', self.get_stats),
                web.get('/', self.about),
            ]
        )

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()
        print(f'Running at {self.host}:{self.port}')
        await asyncio.Event().wait()

    async def about(self, request):
        '''Returns the about me dict'''
        about = {
            'author': 'Stian Langvann',
            'contact': {
                'email': 'stian@langvann.no',
                'phone': '0047 942 47 659',
            },
            'about': (
                'bankid.lazywack.no is an alternative bankid status page to bankid.statuspages.io which doesnt include data'
                ' about mobile bankid. Keeps a 7 day record. Notifies through slack, sms or discord.'
            ),
            'access': 'endpoints are only accessible using api keys. Use contact details above.',
        }
        return web.Response(content_type="application/json", text=str(json.dumps(about, indent=2)), status=200)

    async def auth(self, key):
        '''Creats an Auth Object with information about caller'''
        return Auth(key, self.db)

    async def get_stats_post(self, request):
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:
            await self.stat.authorized()
            data = await request.post()
            add_data = {data[x] for x in data}
            for key in add_data:
                if len(add_data[key]) == 0:
                    return await self.get_stats(request, indata='Not completed properly')

        return await self.unauthorized()

    async def get_stats(self, request, indata=None) -> web.Response:
        '''Api View of different statistics from the database.'''
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
                        'new_key': key.hexdigest(),
                    }

                    return aiohttp_jinja2.render_template('admin.html', request, data)
            except Exception:
                traceback.print_exc()
                return await self.unauthorized()
        return await self.unauthorized()

    async def api(self, request) -> web.Response:
        '''Handles the "api" endpoint, checks with auth and returns an Api Object in dict form.'''
        auth = await self.auth(request.match_info['key'])
        if auth.is_auth:

            await self.stat.authorized()

            # Build the Api endpoint
            response = Api({'auth': 'Authorized'}, self.bidi.api, self.bidi.openapi).__dict__

            # Returns the Api endpoint
            return web.Response(content_type="application/json", text=str(json.dumps(response, indent=2)), status=200)

        # or return the unauthorized message
        return await self.unauthorized()

    async def bankid(self, request):
        '''Handles the "bankid" endpoint. Returns a jinja html template.'''
        auth = await self.auth(request.match_info['key'])
        ts = await self.stat.get_timeline()
        print(ts)
        if auth.is_auth:
            await self.stat.authorized()

            # Returns the Jinja Document
            bankidstatus = self.bidi.get_status()
            data = {'data': bankidstatus.__dict__, 'timeline': self.timeline}
            return aiohttp_jinja2.render_template('bankid.html', request, data, status=200)

        # or returns the unauthorized message
        return await self.unauthorized()

    async def unauthorized(self):
        message = {'message': {'auth': 'Unauthorized'}}

        await self.stat.unauthorized()

        return web.Response(content_type="application/json", text=json.dumps(message, indent=2), status=403)
