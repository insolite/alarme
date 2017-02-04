import asyncio

from .essential import Essential


class ScheduleStop(Exception):
    pass


class Schedule(Essential):

    def __init__(self, app, id_, state, action_descriptor, action_data, run_count=None, run_interval=5, delay=0):
        super().__init__(app, id_)
        self.state = state
        self.action_descriptor = action_descriptor
        self.action_data = action_data
        self.run_count = run_count
        self.run_interval = run_interval
        self.delay = delay
        self.active_action = None
        self._future = None
        self._sleep_future = None

    @property
    def active(self):
        return self.active_action and self.active_action.running

    def _end(self):
        self.logger.info('schedule_end')
        self._future = None
        raise ScheduleStop

    def _end_sleep(self):
        if self._future and not self._future.done():
            self._future.set_result(None)

    async def _sleep(self, delay):
        # TODO: Too complicated, reimplement it
        if not self.active:
            self._end()
        self._future = asyncio.Future()
        self._sleep_future = self.loop.call_later(delay, self._end_sleep)
        try:
            await self._future
        except asyncio.CancelledError:
            self._end()

    def _continue(self, run_count):
        return (self.run_count is None or run_count < self.run_count) and self.active

    async def run(self):
        try:
            self.logger.info('schedule_run')
            self.active_action = self.action_descriptor.construct(**self.action_data)
            self.logger.info('schedule_delay', delay=self.delay)
            await self._sleep(self.delay)
            run_count = 0
            while self._continue(run_count):
                while True:
                    try:
                        await self.active_action.execute()
                    except:
                        await self._sleep(1)
                    else:
                        break
                run_count += 1
                if self._continue(run_count):
                    self.logger.info('schedule_interval', interval=self.run_interval)
                    await self._sleep(self.run_interval)
            self._end()
        except ScheduleStop:
            pass
        finally:
            self.active_action = None

    def stop(self):
        self.logger.info('schedule_stop')
        if self._future:
            self._future.cancel()
        if self._sleep_future:
            self._sleep_future.cancel()
        if self.active:
            self.active_action.stop()
