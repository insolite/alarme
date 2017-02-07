import asyncio

from alarme import Action
from alarme.extras.common import SingleRFDevice


class RfTransmitterAction(Action):

    def __init__(self, app, id_, gpio, code, code_extra=0, run_count=1, run_interval=0.02):
        super().__init__(app, id_)
        self.gpio = gpio
        self.code = code
        self.code_extra = code_extra
        self.run_count = run_count
        self.run_interval = run_interval
        self.rf_device = SingleRFDevice(self.gpio)

    def _continue(self, run_count):
        return self.running and (self.run_count is None or run_count < self.run_count)

    async def run(self):
        self.rf_device.enable_tx()
        try:
            run_count = 0
            while self._continue(run_count):
                self.rf_device.tx_code(self.code + self.code_extra)
                run_count += 1
                if self._continue(run_count):
                    await asyncio.sleep(self.run_interval)
        finally:
            self.rf_device.disable_tx()

    async def cleanup(self):
        await super().cleanup()
        # self.rf_device.cleanup()
