from alarme.core.action import Action
from alarme.extras.common import SingleRFDevice


class RfTransmitterAction(Action):

    def __init__(self, app, name, id_, gpio, code):
        super().__init__(app, name, id_)
        self.gpio = gpio
        self.code = code
        self.rf_device = SingleRFDevice(self.gpio)

    async def run(self):
        try:
            self.rf_device.enable_tx()
            self.rf_device.tx_code(self.code)
        finally:
            self.rf_device.disable_tx()

    async def cleanup(self):
        await super().cleanup()
        # self.rf_device.cleanup()
