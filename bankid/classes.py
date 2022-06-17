from dataclasses import dataclass
from bankid.users import Users
import datetime
import random


@dataclass(frozen=True)
class Status:
    statuscode: int = 0
    meaning: str = 'BIDI initialiseres og vil hente data innen 30 sekunder eller mindre'
    text: str = 'Initialiserer'
    extra: str = ''
    color: str = 'black'
    random: random = random

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
        ''' Gets the user data'''
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

        blocks = {
                [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': 'BankID status update.',
                            'emoji': False
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': 'BankID has a status update '
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f'*When:*\n {datetime.datetime.now()}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Severity:*\n{self.severity}'
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f'*Offending task:*\n{self.task}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Current value:*\n{self.value}'
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f'*Threshold level*\n\n{self.level}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Default value (Historic)*\n{self.historic}'
                            }
                        ]
                    }
                ]
            }
        return blocks
