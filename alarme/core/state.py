import asyncio

from .essential import Essential


class State(Essential):

    def __init__(self, app, name, id_, sensors, reactivatable=True):
        super().__init__(app, name, id_)
        self.sensors = sensors
        self.schedules = {}
        self.reactivatable = reactivatable
        self._schedules_tasks = []

    def add_schedule(self, id_, schedule):
        self.schedules[id_] = schedule

    def remove_action(self, id_):
        self.schedules.pop(id_)

    async def activate(self):
        self.logger.info('state_activate')
        self._schedules_tasks = [asyncio.ensure_future(schedule.run())
                                 for schedule in self.schedules.values()]

    async def deactivate(self):
        self.logger.info('state_deactivate')
        for schedule in self.schedules.values():
            schedule.stop()
        if self._schedules_tasks:
            await asyncio.wait(self._schedules_tasks)
