import asyncio
from dataclasses import dataclass
from slack_sdk.webhook.client import WebhookClient


secrets = {
    '#bankid': 'https://hooks.slack.com/services/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',
    '#bankid-test': 'https://hooks.slack.com/services/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',
}


@dataclass
class Message(object):
    def __init__(self):
        self.content = {}
        self.valid = None

    def set(self, **kwargs):
        '''Sets the rich text message.'''
        blocks = []
        for k, v in kwargs.items():
            markdown = {"type": "section", "text": {"type": "mrkdwn", "text": f"*{k}*\n{v}"}}
            blocks.append(markdown)

        self.content['blocks'] = blocks

        self.valid = True if isinstance(self.content, dict) else False
        if self.valid:
            print(self.content)

    def __repr__(self):
        return str(self.content)

    def __dict__(self):
        return self.content


class Slack:
    '''Slack Webhook integration'''

    instance = None

    def __new__(cls, *args, **kwargs):  # noqa: W0613
        # This class only needs to be called once. Once its called, reuse the exact same class.
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, db):
        self.db = db
        self.webhooks = {}
        for k, v in secrets.items():
            self.webhooks[k] = v

    def _message(self, **kwargs) -> Message:
        '''Returns a message object for rich content messages.'''
        mess = Message()
        mess.set(**kwargs)
        return mess

    def send(self, chan: list, **kwargs) -> bool:
        '''Prepares and sends the message'''

        message = self._message(**kwargs)
        loop = asyncio.get_event_loop()
        for channel in chan:
            if channel in self.webhooks:
                loop.run_in_executor(None, self._send(channel, message))
            else:
                print(f'{channel} is not a valid channel')
        return True

    def _send(self, chan: str, message: Message):
        '''Sends the message through _sendmessage in executor to ensure we dont spend time waiting for results.'''
        webhook = WebhookClient(self.webhooks[chan])
        response = webhook.send(blocks=message.content['blocks'])
        if response.status_code == 200 and response.body == 'ok':
            print(f'Message sendt to {chan}')
        else:
            print(f'Unable to send message to {chan}, response status {response.status_code}, error: {response.body}')


class Run:
    def __init__(self):
        self.slack = Slack()

    async def run(self):

        self.slack.send(['#bankid', '#slack'], test=123, something='here', wonderful='to_meet_you')
