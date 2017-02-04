from .gsm_action import GsmAction


class CallAction(GsmAction):

    def __init__(self, app, id_, serial_url, number, seconds):
        super().__init__(app, id_, serial_url)
        self.number = number
        self.seconds = seconds

    async def run(self):
        self.logger.info('make_call')
        await self.gsm_modem.call(self.number, self.seconds)
