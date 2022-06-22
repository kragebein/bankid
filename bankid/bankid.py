from bankid.stats import Timeline
import requests
import time
import asyncio

from typing import Any
from bs4 import BeautifulSoup
from bankid.classes import Status
from bankid.warden import Warden


class BankID:
    def __init__(self, stats):
        self.stats = stats
        self.log = Warden()
        self.status = Status()
        self.timeline = Timeline()
        self.openapi = {}
        self.api = {'Init': 'initializing'}
        self.url = 'https://www.bankid.no/status'
        self.code: dict = {
            1: {
                'meaning': 'Bankid har grønne lamper, alt er tut og kjør!',
                'text': 'BankID: Alt virker.',
                'color': 'green',
                'field': '<span class="color-dot none">',
            },
            2: {
                'meaning': 'Gul lampe. Betyr tregheter eller at noe er nede.',
                'text': 'BankID: Delvis nede.',
                'color': 'yellow',
                'field': '<span class="color-dot minor">',
            },
            3: {
                'meaning': 'En eller flere tjenester hos bankID eller Underleverandører er nede',
                'text': 'BankID: delvis nede.',
                'color': 'orange',
                'field': '<span class="color-dot major">',
            },
            4: {
                'meaning': 'Rødt lys hos BankID. Alle tjenester er utilgjengelige.',
                'text': 'BankID: er helt nede.',
                'color': 'red',
                'field': '<span class="color-dot critical">',
            },
            5: {
                'meaning': 'BankID er helt eller delvis utilgjengelig på grunn av planlagt vedlikehold.',
                'text': 'BankID: Vedlikehold.',
                'color': 'blue',
                'field': '<span class="color-dot maintenance">',
            },
            9: {
                'meaning': 'En feil gjør at dette BIDI ikke klarer innehente ny data fra BankID.no\nKontakt IT.',
                'text': 'BIDI: Error 9.',
                'color': 'black',
                'field': '11111111111111111111111111111111111',
            },
        }
        self.refresh = 30
        self.lastupdate = int(time.time())

    async def update(self) -> None:

        bankid_data = await self.from_bankid()
        status = await self.parsedata(bankid_data)
        await self.updatestatus(status, bankid_data)

    async def parsedata(self, data: str) -> int:
        if data is None:
            return 9
        soup = BeautifulSoup(data, 'html.parser')
        for _data in soup.find_all("div", {"class": "m-statuspage"}):
            _data = str(_data)
            _data = _data.replace('\n', '')

            for code in self.code:
                if self.code[code]['field'] in _data:
                    self.log.info('Status retrieved', code=code)
                    return code
        # Return error code we couldnt find 'field' data.
        return 9

    async def updateloop(self) -> None:
        '''Loop that runs update every 30 seconds.'''
        timer = int(time.time())
        while True:
            if timer < int(time.time()):
                await self.update()
                timer += 60
            await asyncio.sleep(1)

    async def updatestatus(self, code: int, data: str) -> None:
        '''Updating the web view, api and db with status change.'''
        extra = None if code in [1, 9] else await self.get_extra(data)

        # if code != self.status.statuscode and code not in [1, 9]:
        # await self.stats.changestatus(self.code[code]['color'], extra)

        self.status = Status(
            int(code),
            self.code[code]['meaning'],
            self.code[code]['text'],
            extra,
            self.code[code]['color'],
        )

        # Updates the timeline
        status_text = extra if extra is not None else self.code[code]['text']
        self.timeline.put(status_text, self.code[code]['color'])

        self.api = {
            'bidi': {
                'status': int(code),
                'color': self.code[code]['color'],
                'text': self.code[code]['text'],
                'extra': extra,
                'meaning': self.code[code]['meaning'],
            }
        }

        self.openapi = await self.statuspages()

    async def statuspages(self):
        url = 'https://bankid-services.statuspage.io/'
        header = {'Accept': 'application/json'}
        response = {'Error': 'Couldnt retrieve data from statuspages.'}
        try:
            r = requests.get(url, headers=header)
            if r.status_code == 200:
                return r.json()
        except Exception:  # noqa: W0703
            self.stats.errors()
            self.log.exception('Exception occured while retrieving data from bankid-services.statuspage.io')
            return response

    async def get_extra(self, data: str) -> Any:
        ret = None
        soup = BeautifulSoup(data, 'html.parser')
        _data = soup.find_all("div", {"class": "m-statuspage-description"})
        for x in _data:
            ret = x.find_next("p").get_text().replace('\n', '').replace('\r', '').strip()
        return ret if ret is not None else '\nKunne ikke innhente detaljert informasjon om bankidfeil.'

    async def from_bankid(self) -> str:
        try:
            r = requests.get(self.url, allow_redirects=True)
            if r:
                return r.content
            else:
                return None
        except requests.exceptions.RequestException:
            self.log.exception('Unable to retrieve data from bankid.no')
            await self.stats.errors()
            return None

    def get_status(self) -> Status:
        return self.status
