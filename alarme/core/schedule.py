import asyncio

from .essential import Essential


class ScheduleStop(Exception):
    pass


class Schedule(Essential):

    def __init__(self, app, id_, state, run_count=None, run_interval=5, delay=0):
        super().__init__(app, id_)
        self.state = state
        self.run_count = run_count
        self.run_interval = run_interval
        self.delay = delay
        self.actions = []
        self.active_action = None
        self._future = None
        self._sleep_future = None
        self.running = False

    def add_action(self, action_descriptor):
        self.actions.append(action_descriptor)

    def _end(self):
        self.logger.info('schedule_end')
        self._future = None
        raise ScheduleStop

    def _end_sleep(self):
        if self._future and not self._future.done():
            self._future.set_result(None)

    async def _sleep(self, delay):
        # TODO: Too complicated, reimplement it
        if not self.running:
            self._end()
        self._future = asyncio.Future()
        self._sleep_future = self.loop.call_later(delay, self._end_sleep)
        try:
            await self._future
        except asyncio.CancelledError:
            self._end()

    def _continue(self, run_count):
        return (self.run_count is None or run_count < self.run_count) and self.running

    async def run_actions(self):
        for action_descriptor in self.actions:
            self.active_action = action_descriptor.construct()
            try:
                while self.running:
                    try:
                        await self.active_action.execute()
                    except:
                        await self._sleep(1)
                    else:
                        break
            finally:
                self.active_action = None
            if not self.running:
                break

    async def run(self):
        self.logger.info('schedule_run', delay=self.delay)
        self.running = True
        try:
            await self._sleep(self.delay)
            run_count = 0
            while self._continue(run_count):
                await self.run_actions()
                run_count += 1
                if self._continue(run_count):
                    self.logger.info('schedule_interval', interval=self.run_interval)
                    await self._sleep(self.run_interval)
            self._end()
        except ScheduleStop:
            pass
        finally:
            self.running = False

    def stop(self):
        self.logger.info('schedule_stop')
        if self._future:
            self._future.cancel()
        if self._sleep_future:
            self._sleep_future.cancel()
        if self.active_action:
            self.active_action.stop()
        self.running = False
