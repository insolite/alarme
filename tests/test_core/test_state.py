import asyncio
from unittest.mock import MagicMock

from asynctest import CoroutineMock

from alarme import State
from tests.common import BaseTest


class StateTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.sensor1 = MagicMock()
        self.sensor2 = MagicMock()
        self.sensors = {self.sensor1.id: self.sensor1, self.sensor2.id: self.sensor2}
        self.reactivatable = False
        self.state = State(self.app, self.id, self.sensors, self.reactivatable)

    def test_add_schedule__fresh(self):
        id_ = MagicMock()
        schedule = MagicMock()

        self.state.add_schedule(id_, schedule)

        self.assertEqual(self.state.schedules, {id_: schedule})

    def test_add_schedule__exists(self):
        id1 = MagicMock()
        id2 = MagicMock()
        schedule1 = MagicMock()
        schedule2 = MagicMock()
        self.state.schedules = {id1: schedule1}

        self.state.add_schedule(id2, schedule2)

        self.assertEqual(self.state.schedules, {id1: schedule1, id2: schedule2})

    def test_add_behaviour__fresh(self):
        sensor_id = MagicMock()
        code = MagicMock()
        action_descriptor = MagicMock()

        self.state.add_behaviour(sensor_id, code, action_descriptor)

        self.assertEqual(self.state.behaviours, {sensor_id: {code: [action_descriptor]}})


    def test_add_behaviour__same_code_exists(self):
        sensor_id = MagicMock()
        code = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.state.behaviours = {sensor_id: {code: [action_descriptor1]}}

        self.state.add_behaviour(sensor_id, code, action_descriptor2)

        self.assertEqual(self.state.behaviours, {sensor_id: {code: [action_descriptor1, action_descriptor2]}})

    def test_add_behaviour__another_code_exists(self):
        sensor_id = MagicMock()
        code1 = MagicMock()
        code2 = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.state.behaviours = {sensor_id: {code1: [action_descriptor1]}}

        self.state.add_behaviour(sensor_id, code2, action_descriptor2)

        self.assertEqual(self.state.behaviours, {sensor_id: {code1: [action_descriptor1], code2: [action_descriptor2]}})

    def test_add_behaviour__another_sensor_exists(self):
        sensor_id1 = MagicMock()
        sensor_id2 = MagicMock()
        code1 = MagicMock()
        code2 = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.state.behaviours = {sensor_id1: {code1: [action_descriptor1]}}

        self.state.add_behaviour(sensor_id2, code2, action_descriptor2)

        self.assertEqual(self.state.behaviours, {sensor_id1: {code1: [action_descriptor1]}, sensor_id2: {code2: [action_descriptor2]}})

    def test_activate(self):
        self.state.running = False
        schedule1 = MagicMock()
        schedule1.run = CoroutineMock()
        schedule2 = MagicMock()
        schedule2.run = CoroutineMock()
        schedules = {schedule1.id: schedule1, schedule2.id: schedule2}
        self.state.schedules = schedules

        self.loop.run_until_complete(self.state.activate())

        self.assertTrue(self.state.running)
        for task in self.state._schedules_tasks:
            self.assertIsInstance(task, asyncio.Task)

    def test_deactivate__full(self):
        self.state.running = True
        self.state.active_action = MagicMock()
        schedule1 = MagicMock()
        schedule1.run = CoroutineMock()
        schedule2 = MagicMock()
        schedule2.run = CoroutineMock()
        schedules = {schedule1.id: schedule1, schedule2.id: schedule2}
        self.state.schedules = schedules
        for schedule in schedules.values():
            self.state._schedules_tasks.append(asyncio.ensure_future(schedule.run()))

        self.loop.run_until_complete(self.state.deactivate())

        self.assertFalse(self.state.running)
        self.state.active_action.stop.assert_called_once_with()
        for schedule in schedules.values():
            schedule.stop.assert_called_once_with()
        for task in self.state._schedules_tasks:
            self.assertTrue(task.done())

    def test_deactivate__none(self):
        self.state.running = True
        self.state.active_action = None
        self.state.schedules = {}

        self.loop.run_until_complete(self.state.deactivate())

        self.assertFalse(self.state.running)

    def test_sensor_react__fine(self):
        self.state.running = True
        sensor = MagicMock()
        code = MagicMock()
        action_result = MagicMock()
        action = MagicMock()
        action.execute = CoroutineMock(return_value=action_result)
        action_descriptor = MagicMock()
        action_descriptor.construct = MagicMock(return_value=action)
        behaviour = [action_descriptor]

        result = self.loop.run_until_complete(self.state.sensor_react(sensor, code, behaviour))

        self.assertEqual(result, [action_result])
        self.assertIsNone(self.state.active_action)
        action_descriptor.construct.assert_called_once_with()
        action.execute.assert_called_once_with()

    def test_sensor_react__exception(self):
        self.state.running = True
        sensor = MagicMock()
        code = MagicMock()
        action = MagicMock()
        action.execute = CoroutineMock(side_effect=Exception)
        action_descriptor = MagicMock()
        action_descriptor.construct = MagicMock(return_value=action)
        behaviour = [action_descriptor]

        result = self.loop.run_until_complete(self.state.sensor_react(sensor, code, behaviour))

        self.assertEqual(result, [])
        self.assertIsNone(self.state.active_action)
        action_descriptor.construct.assert_called_once_with()
        action.execute.assert_called_once_with()

    def test_sensor_react__stop(self):
        self.state.running = True
        sensor = MagicMock()
        code = MagicMock()
        action_result1 = MagicMock()
        def stop():
            self.state.running = False
            return action_result1
        action1 = MagicMock()
        action1.execute = CoroutineMock(side_effect=stop)
        action_descriptor1 = MagicMock()
        action_descriptor1.construct = MagicMock(return_value=action1)
        action_result2 = MagicMock()
        action2 = MagicMock()
        action2.execute = CoroutineMock(return_value=action_result2)
        action_descriptor2 = MagicMock()
        action_descriptor2.construct = MagicMock(return_value=action2)
        behaviour = [action_descriptor1, action_descriptor2]

        result = self.loop.run_until_complete(self.state.sensor_react(sensor, code, behaviour))

        self.assertEqual(result, [action_result1])
        self.assertIsNone(self.state.active_action)
        action_descriptor1.construct.assert_called_once_with()
        action1.execute.assert_called_once_with()
        action_descriptor2.construct.assert_not_called()
        action2.execute.assert_not_called()

    def test_notify__react(self):
        sensor = MagicMock()
        code = MagicMock()
        behaviour = MagicMock()
        react_result = MagicMock()
        self.state.sensors = {sensor.id: sensor}
        self.state.get_behaviour = MagicMock(return_value=behaviour)
        self.state.sensor_react = CoroutineMock(return_value=react_result)

        result = self.loop.run_until_complete(self.state.notify(sensor, code))

        self.assertEqual(result, react_result)
        self.state.get_behaviour.assert_called_once_with(sensor, code)
        self.state.sensor_react.assert_called_once_with(sensor, code, behaviour)

    def test_notify__ignore_no_behaviour(self):
        sensor = MagicMock()
        code = MagicMock()
        self.state.sensors = {sensor.id: sensor}
        self.state.get_behaviour = MagicMock(return_value=None)
        self.state.sensor_react = CoroutineMock()

        result = self.loop.run_until_complete(self.state.notify(sensor, code))

        self.assertIsNone(result)
        self.state.get_behaviour.assert_called_once_with(sensor, code)
        self.state.sensor_react.assert_not_called()

    def test_notify__ignore_no_sensor(self):
        sensor = MagicMock()
        code = MagicMock()
        self.state.sensors = {}
        self.state.get_behaviour = MagicMock()
        self.state.sensor_react = CoroutineMock()

        result = self.loop.run_until_complete(self.state.notify(sensor, code))

        self.assertIsNone(result)
        self.state.get_behaviour.assert_not_called()
        self.state.sensor_react.assert_not_called()

    def test_get_behaviour__sensor(self):
        sensor = MagicMock()
        code = MagicMock()
        expected_behaviour = MagicMock()
        sensor.behaviours = {code: expected_behaviour}
        self.state.behaviours = {}

        behaviour = self.state.get_behaviour(sensor, code)

        self.assertEqual(behaviour, expected_behaviour)

    def test_get_behaviour__sensor_another_code(self):
        sensor = MagicMock()
        code = MagicMock()
        another_code = MagicMock()
        special_behaviour = MagicMock()
        expected_behaviour = MagicMock()
        sensor.behaviours = {code: expected_behaviour}
        self.state.behaviours = {sensor.id: {another_code: special_behaviour}}

        behaviour = self.state.get_behaviour(sensor, code)

        self.assertEqual(behaviour, expected_behaviour)

    def test_get_behaviour__state(self):
        sensor = MagicMock()
        code = MagicMock()
        native_behaviour = MagicMock()
        expected_behaviour = MagicMock()
        sensor.behaviours = {code: native_behaviour}
        self.state.behaviours = {sensor.id: {code: expected_behaviour}}

        behaviour = self.state.get_behaviour(sensor, code)

        self.assertEqual(behaviour, expected_behaviour)
