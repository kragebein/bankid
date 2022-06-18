from dataclasses import dataclass
from bankid.users import Users
import datetime


@dataclass(frozen=True)
class Status:
    statuscode: int = 0
    meaning: str = 'BIDI initialiseres og vil hente data innen 30 sekunder eller mindre'
    text: str = 'Initialiserer'
    extra: str = ''
    color: str = 'black'

    def __repr__(self):
        return self.statuscode

    def __eq__(self, code):
        return code == self.statuscode


@dataclass
class Auth:
    is_auth: bool = False
    user: dict = None

    def __init__(self, key, db):
        self.x = Users(db)
        if self.x.check(key):
            timestamp = f'[{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] '
            print(timestamp, self.x.user)
            self.is_auth = True
            self.user = self.x.user

    def get(self):
        '''Gets the user data'''
        if not self.is_auth:
            return []
        return self.user

    def __str__(self):
        return self.is_auth

    def __repr__(self):
        return self.is_auth


@dataclass
class Api:
    message: str = None
    bidi: str = None
    openapi: str = None


@dataclass
class statusUpdate:
    def __init__(self, status):
        self.status = status

    def block(self):

        return {
            [
                {'type': 'header', 'text': {'type': 'plain_text', 'text': 'BankID status update.', 'emoji': False}},
                {'type': 'section', 'fields': [{'type': 'mrkdwn', 'text': 'BankID has a status update '}]},
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': f'*When:*\n {datetime.datetime.now()}'},
                        {'type': 'mrkdwn', 'text': '*Severity:*\n'},
                    ],
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': '*Offending task:*\n'},
                        {'type': 'mrkdwn', 'text': '*Current value:*\n'},
                    ],
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': '*Threshold level*\n\n'},
                        {'type': 'mrkdwn', 'text': '*Default value (Historic)*\n'},
                    ],
                },
            ]
        }
