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

    def test_add_schedule__another_schedule_exists(self):
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

    def test_deactivate__empty(self):
        self.state.running = True
        self.state.active_action = None
        self.state.schedules = {}

        self.loop.run_until_complete(self.state.deactivate())

        self.assertFalse(self.state.running)
