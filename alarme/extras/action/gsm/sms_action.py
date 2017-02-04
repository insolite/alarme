from .gsm_action import GsmAction


class SmsAction(GsmAction):

    def __init__(self, app, id_, serial_url, number, text, timeout=20):
        super().__init__(app, id_, serial_url)
        self.number = number
        self.text = text
        self.timeout = timeout

    async def run(self):
        self.logger.info('send_sms')
        await self.gsm_modem.send_sms(self.number, self.text, self.timeout)
