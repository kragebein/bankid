
import json
import sys
from json.decoder import JSONDecodeError

class Config():

    def read(self, top):
        try:
            with open('config.json', 'r') as configuration:
                data = json.loads(configuration.read())
                top.host = data['webserver']['host']
                top.port = data['webserver']['port']
                
                top.bidi.refresh = data['refresh_time']
        except JSONDecodeError as E:
            print(f'Misconfigured config: {E}')
            sys.exit(1)
        except FileNotFoundError as E:
            print(f'Configuration file not found: {E}')
            sys.exit(1)
        except AttributeError as E:
            print('AttributeError: {E}')