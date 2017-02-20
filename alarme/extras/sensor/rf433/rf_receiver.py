import asyncio

from alarme import Sensor
from alarme.extras.common import SingleRFDevice


class RfReceiverSensor(Sensor):

    def __init__(self, app, id_, gpio, code, check_interval=0.1):
        super().__init__(app, id_)
        self.gpio = gpio
        self.code = code
        self.check_interval = check_interval
        self.rf_device = SingleRFDevice(self.gpio)

    async def process_code(self, raw_code):
        event = raw_code ^ self.code
        if event in self.behaviours:
            await self.notify(event)

    async def cleanup(self):
        await super().cleanup()
        # self.rf_device.cleanup()

    async def run(self):
        self.rf_device.enable_rx()
        try:
            timestamp = self.rf_device.rx_code_timestamp
            while self.running:
                if self.rf_device.rx_code_timestamp != timestamp:
                    timestamp = self.rf_device.rx_code_timestamp
                    raw_code = self.rf_device.rx_code
                    self.logger.debug('checking_signal',
                                      raw_code=raw_code,
                                      pulselength=self.rf_device.rx_pulselength,
                                      protocol=self.rf_device.rx_proto)
                    await self.process_code(raw_code)
                await asyncio.sleep(self.check_interval)
        finally:
            self.rf_device.disable_rx()
