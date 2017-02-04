import asyncio

from alarme.core.sensor import Sensor
from alarme.extras.common import SingleRFDevice


class RfReceiverSensor(Sensor):

    def __init__(self, app, name, id_, gpio, code):
        super().__init__(app, name, id_)
        self.gpio = gpio
        self.code = code
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
            await asyncio.sleep(0.5)
        self.rf_device.disable_rx()
