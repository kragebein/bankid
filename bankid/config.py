import json
from json.decoder import JSONDecodeError
from bankid.warden import Warden

log = Warden()


class Config:
    def read(self, top):
        log.debug('Loading configuration')
        try:
            with open('config.json', 'r', encoding='UTF-8') as configuration:
                data = json.loads(configuration.read())
                top.host = data['webserver']['host']
                top.port = data['webserver']['port']
                top.bidi.refresh = data['refresh_time']
        except JSONDecodeError:
            log.exception('Couldnt decode json data')
        except FileNotFoundError:
            log.exception('Configuration file not found!')
        except AttributeError:
            log.exception('Invalid data in the configuration file')
