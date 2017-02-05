import asyncio

from .essential import Essential


class State(Essential):

    def __init__(self, app, id_, sensors, reactivatable=True):
        super().__init__(app, id_)
        self.sensors = sensors
        self.schedules = {}
        self.behaviours = {}
        self.reactivatable = reactivatable
        self._schedules_tasks = []
        self.running = False
        self.active_action = None

    def add_schedule(self, id_, schedule):
        self.schedules[id_] = schedule

    def add_behaviour(self, sensor_id, code, action_descriptor):
        self.behaviours.setdefault(sensor_id, {}).setdefault(code, []).append(action_descriptor)

    async def activate(self):
        self.logger.info('state_activate')
        self.running = True
        self._schedules_tasks = [asyncio.ensure_future(schedule.run())
                                 for schedule in self.schedules.values()]

    async def deactivate(self):
        self.logger.info('state_deactivate')
        self.running = False
        if self.active_action:
            self.active_action.stop()
        for schedule in self.schedules.values():
            schedule.stop()
        if self._schedules_tasks:
            await asyncio.wait(self._schedules_tasks)

    async def sensor_react(self, sensor, code, behaviour):
        logger = self.logger.bind(sensor=sensor.id, code=code)
        logger.info('sensor_react')
        result = []
        try:
            for action_descriptor in behaviour:
                self.active_action = action_descriptor.construct()
                try:
                    result.append(await self.active_action.execute())
                except:
                    pass  # TODO: Try again as in schedule?
                if not self.running:
                    break
        finally:
            self.active_action = None
        return result

    async def notify(self, sensor, code):
        logger = self.logger.bind(sensor=sensor.id, code=code)
        if sensor in self.sensors.values():
            behaviour = self.get_behaviour(sensor, code)
            if behaviour:
                return await self.sensor_react(sensor, code, behaviour)
            else:
                logger.error('notify_ignore', reason='unknown_behaviour')
        else:
            logger.info('notify_ignore', reason='sensor_not_listed_for_state')

    def get_behaviour(self, sensor, code):
        special_behaviour = self.behaviours.get(sensor.id, {}).get(code)
        return special_behaviour or sensor.behaviours.get(code)
