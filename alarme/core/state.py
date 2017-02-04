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

    def add_schedule(self, id_, schedule):
        self.schedules[id_] = schedule

    def remove_action(self, id_):
        self.schedules.pop(id_)

    def add_behaviour(self, sensor_id, code, action_descriptor, action_data):
        self.behaviours.setdefault(sensor_id, {}).setdefault(code, []).append((action_descriptor, action_data))

    def remove_behaviour(self, sensor_id):
        self.behaviours.pop(sensor_id)

    async def activate(self):
        self.logger.info('state_activate')
        self._schedules_tasks = [asyncio.ensure_future(schedule.run())
                                 for schedule in self.schedules.values()]

    async def deactivate(self):
        self.logger.info('state_deactivate')
        for schedule in self.schedules.values():
            schedule.stop()
        # TODO: stop and wait executing actions in self.notify()
        if self._schedules_tasks:
            await asyncio.wait(self._schedules_tasks)

    async def notify(self, sensor, code):
        logger = self.logger.bind(sensor=sensor.id, code=code)
        if sensor in self.sensors.values():
            special_behavior = self.behaviours.get(sensor.id, {}).get(code)
            behaviour = special_behavior or sensor.behaviours.get(code)
            if behaviour:
                logger.info('sensor_react')
                for action_descriptor, action_data in behaviour:
                    action = action_descriptor.construct(**action_data)
                    if action:
                        try:
                            await action.execute()
                        except:
                            pass # TODO: Try again as in schedule?
                    else:
                        logger.error('sensor_unknown_action')
                    # TODO: break if not self.running
            else:
                logger.error('sensor_unknown_behaviour', behaviour=behaviour, special_behavior=special_behavior)
        else:
            logger.info('notify_ignore', reason='sensor_not_listed_for_state')
