from gsm_modem_asyncio import GsmModem

from alarme import Action


class SingleGsmModemMeta(type):

    instances = {}

    def __call__(mcs, serial_url, *args, **kwargs):
        if serial_url not in mcs.instances:
            mcs.instances[serial_url] = super().__call__(serial_url, *args, **kwargs)
        return mcs.instances[serial_url]


class SingleGsmModem(GsmModem, metaclass=SingleGsmModemMeta):
    pass


class GsmAction(Action):

    def __init__(self, app, id_, serial_url):
        super().__init__(app, id_)
        self.serial_url = serial_url
        self.gsm_modem = SingleGsmModem(self.serial_url)

    async def run(self):
        raise NotImplementedError
