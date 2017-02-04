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


def get_default_name(klass, id_):
    return 'Unnamed {}[{}]'.format(klass.__name__, id_)


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
                name = action_data.pop('name', get_default_name(action_class, action_id))
                action = default_action_descriptor_factory(self, action_id, action_class, **action_data)
                self.add_action_descriptor(action_id, action)

        for sensor_id, sensor_data in config.get('sensors', {}).items():
            sensor_class = import_class(sensor_data.pop('class'))
            name = sensor_data.pop('name', get_default_name(sensor_class, sensor_id))
            behaviours = sensor_data.pop('behaviours', {})
            sensor = sensor_class(self, sensor_id, **sensor_data)
            for code, behaviour in behaviours.items():
                action_id = behaviour.pop('id')
                sensor.add_behaviour(code, self.action_descriptors[action_id], behaviour)
            self.add_sensor(sensor_id, sensor)

        for state_id, state_data in config.get('states', {}).items():
            state_class = default_state_factory
            name = state_data.pop('name', get_default_name(state_class, state_id))
            sensors = {}
            behaviours = []
            for sensor in state_data.pop('sensors', []):
                if isinstance(sensor, dict):
                    sensor_id = sensor['id']
                    for behaviour_code, action_data in sensor['behaviours'].items():
                        action_id = action_data.pop('id')
                        behaviours.append((sensor_id, behaviour_code, self.action_descriptors[action_id], action_data))
                else:
                    sensor_id = sensor
                sensors[sensor_id] = self.sensors[sensor_id]
            schedules_data = state_data.pop('schedules', {})
            state = state_class(self, state_id, sensors, **state_data)
            for behaviour in behaviours:
                state.add_behaviour(*behaviour)
            for schedule_id, schedule_data in schedules_data.items():
                schedule_class = default_schedule_factory
                name = schedule_data.pop('name', get_default_name(schedule_class, schedule_id))
                action_data = schedule_data.pop('action')
                action_id = action_data.pop('id')
                schedule = schedule_class(self, schedule_id, state, self.action_descriptors[action_id], action_data, **schedule_data)
                state.add_schedule(schedule_id, schedule)
            self.add_state(state_id, state)

        await self.set_state(self.states[config['initial_state']])

    def exception_handler(self, exception):
        if self._exception_handler:
            return self._exception_handler(exception)
        raise exception

    def add_sensor(self, id_, sensor):
        self.sensors[id_] = sensor

    def remove_sensor(self, id_):
        self.sensors.pop(id_)

    def add_state(self, id_, state):
        self.states[id_] = state

    def remove_state(self, id_):
        self.states.pop(id_)

    async def set_state(self, state):
        real = self.state != state or state.reactivatable
        self.logger.info('set_state', state=state.id, old_state=self.state.id if self.state else None, ignore=not real)
        if real:
            if self.state:
                await self.state.deactivate()
            self.state = state
            await self.state.activate()

    def add_action_descriptor(self, id_, action_descriptor):
        self.action_descriptors[id_] = action_descriptor

    def remove_action_descriptor(self, id_):
        self.action_descriptors.pop(id_)

    async def run(self):
        self.logger.info('application_start')
        sensor_tasks = [asyncio.ensure_future(sensor.run_forever())
                        for sensor in self.sensors.values()]
        self._app_run_future = asyncio.Future()
        await self._app_run_future
        self._app_run_future = None
        # TODO: notify action stop
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
            await self.state.notify(sensor, code)
        else:
            self.logger.info('notify_ignore', reason='no_active_state')
