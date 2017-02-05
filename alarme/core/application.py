import asyncio
from importlib import import_module

import yaml
from structlog import get_logger

from .state import State
from .action_descriptor import ActionDescriptor
from .schedule import Schedule


def import_class(class_str):
    module_name, class_name = class_str.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, class_name)


def expand_actions(action_descriptors, actions):
    result = []
    if not isinstance(actions, (list, tuple)):
        actions = [actions]
    for action in actions:
        if not isinstance(action, dict):
            action = {'id': action}
        action_id = action.pop('id')
        action_data = action
        result.append(action_descriptors[action_id].clone(**action_data))
    return result


class Application:

    def __init__(self, exception_handler=None):
        self._exception_handler = exception_handler
        self.sensors = {}
        self.states = {}
        self.action_descriptors = {}
        self.state = None
        self.logger = get_logger()
        self.loop = asyncio.get_event_loop()
        self._app_run_future = None

    async def load_config(self, config_path,
                          default_state_factory=State,
                          default_action_descriptor_factory=ActionDescriptor,
                          default_schedule_factory=Schedule):
        with open(config_path) as config_file:
            config = yaml.load(config_file)

        for action_id, action_data in config.get('actions', {}).items():
            abstract = action_data.pop('abstract', False)
            if not abstract:
                action_class = import_class(action_data.pop('class'))
                action = default_action_descriptor_factory(self, action_id, action_class, **action_data)
                self.add_action_descriptor(action_id, action)

        for sensor_id, sensor_data in config.get('sensors', {}).items():
            sensor_class = import_class(sensor_data.pop('class'))
            behaviours = sensor_data.pop('behaviours', {})
            sensor = sensor_class(self, sensor_id, **sensor_data)
            for code, actions in behaviours.items():
                for action_descriptor in expand_actions(self.action_descriptors, actions):
                    sensor.add_behaviour(code, action_descriptor)
            self.add_sensor(sensor_id, sensor)

        for state_id, state_data in config.get('states', {}).items():
            state_class = default_state_factory
            sensors = {}
            behaviours = []
            for sensor in state_data.pop('sensors', []):
                if isinstance(sensor, dict):
                    sensor_id = sensor['id']
                    for behaviour_code, actions in sensor['behaviours'].items():
                        for action_descriptor in expand_actions(self.action_descriptors, actions):
                            behaviours.append((sensor_id, behaviour_code, action_descriptor))
                else:
                    sensor_id = sensor
                sensors[sensor_id] = self.sensors[sensor_id]
            schedules_data = state_data.pop('schedules', {})
            state = state_class(self, state_id, sensors, **state_data)
            for behaviour in behaviours:
                state.add_behaviour(*behaviour)
            for schedule_id, schedule_data in schedules_data.items():
                schedule_class = default_schedule_factory
                actions = schedule_data.pop('actions')
                schedule = schedule_class(self, schedule_id, state, **schedule_data)
                for action_descriptor in expand_actions(self.action_descriptors, actions):
                    schedule.add_action(action_descriptor)
                state.add_schedule(schedule_id, schedule)
            self.add_state(state_id, state)

        await self.set_state(self.states[config['initial_state']])

    def exception_handler(self, exception):
        if self._exception_handler:
            return self._exception_handler(exception)
        raise exception

    def add_sensor(self, id_, sensor):
        self.sensors[id_] = sensor

    def add_state(self, id_, state):
        self.states[id_] = state

    def add_action_descriptor(self, id_, action_descriptor):
        self.action_descriptors[id_] = action_descriptor

    async def set_state(self, state):
        real = self.state != state or state.reactivatable
        self.logger.info('set_state', state=state.id, old_state=self.state.id if self.state else None, ignore=not real)
        if real:
            if self.state:
                await self.state.deactivate()
            self.state = state
            await self.state.activate()

    async def run(self):
        self.logger.info('application_start')
        sensor_tasks = [asyncio.ensure_future(sensor.run_forever())
                        for sensor in self.sensors.values()]
        self._app_run_future = asyncio.Future()
        await self._app_run_future
        self._app_run_future = None
        for sensor in self.sensors.values():
            sensor.stop()
        await asyncio.wait(sensor_tasks)
        if self.state:
            await self.state.deactivate()
        self.logger.info('application_end')

    def stop(self):
        self.logger.info('application_stop')
        if self._app_run_future:
            self._app_run_future.set_result(None)

    async def notify(self, sensor, code):
        if self.state:
            return await self.state.notify(sensor, code)
        self.logger.info('notify_ignore', reason='no_active_state')
