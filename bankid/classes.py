from dataclasses import dataclass
from bankid.users import Users

@dataclass(frozen=True)
class Status:
    statuscode:int = 0
    meaning:str = 'BIDI initialiseres og vil hente data innen 30 sekunder eller mindre'
    text:str = 'Initialiserer'
    extra:str = ''
    color:str = 'black'
    
    def __repr__(self):
        return self.statuscode

    def __eq__(self, code):
        return code == self.statuscode


@dataclass
class Auth:
    is_authorized: bool = None
    user: dict = None

    def __init__(self, key):
        x = Users()
        self.key = key
        if self.key in x.userlist:
            self.user = x.userlist[self.key]
            self.is_authorized = True


    def __str__(self):
        return self.is_authorized

    def __repr__(self):
        return self.is_authorized
    

@dataclass
class Api:
    message: str = None
    bidi: str = None
    openapi: str = None

