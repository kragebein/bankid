
import json
from json.decoder import JSONDecodeError


class Config():

    def read(self, top):
        try:
            with open('config.json', 'r', encoding='UTF-8') as configuration:
                data = json.loads(configuration.read())
                top.host = data['webserver']['host']
                top.port = data['webserver']['port']
                top.bidi.refresh = data['refresh_time']
                print(top)
        except JSONDecodeError as e:
            raise Exception(f'Could not read config: {e}') from e
        except FileNotFoundError as e:
            raise Exception('File not Found') from e
        except AttributeError as e:
            raise AttributeError(f'AttributeError: {e}') from e
