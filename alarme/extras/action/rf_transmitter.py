from alarme import Action
from alarme.extras.common import SingleRFDevice


class RfTransmitterAction(Action):

    def __init__(self, app, id_, gpio, code):
        super().__init__(app, id_)
        self.gpio = gpio
        self.code = code
        self.rf_device = SingleRFDevice(self.gpio)

    async def run(self):
        self.rf_device.enable_tx()
        try:
            self.rf_device.tx_code(self.code)
        finally:
            self.rf_device.disable_tx()

    async def cleanup(self):
        await super().cleanup()
        # self.rf_device.cleanup()
