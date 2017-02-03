import asyncio

from .essential import Essential


class Sensor(Essential):

    def __init__(self, app, name, id_, behaviours):
        super().__init__(app, name, id_)
        self.behaviours = behaviours
        self.running = True

    async def run_forever(self):
        while self.running:
            self.logger.info('sensor_run')
            try:
                await self.run()
            except:
                self.logger.error('sensor_crash', exc_info=True)
                await asyncio.sleep(1)
            else:
                self.logger.info('sensor_end')
        await self.cleanup()

    async def run(self):
        while self.running:
            await asyncio.sleep(0.1)

    def stop(self):
        self.logger.info('sensor_stop')
        self.running = False

    async def cleanup(self):
        self.logger.info('sensor_cleanup')

    async def notify(self, code):
        self.logger.info('sensor_notify', code=code)
        await self.app.notify(self, code)
