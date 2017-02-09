import asyncio
import os.path
from unittest.mock import MagicMock

from asynctest import CoroutineMock

import alarme
from alarme import Application
from tests.common import BaseTest


class ApplicationTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.application = Application()

    def test_load_config(self):
        package_path, = alarme.__path__
        config_path = os.path.join(package_path, '..', 'config_examples', 'full')

        self.loop.run_until_complete(
            self.application.load_config(config_path)
        )

        # TODO: Add assertions and tests with different input

    def test_exception_handler__handle(self):
        exception = MagicMock()
        expected_result = MagicMock()
        self.application._exception_handler = MagicMock(return_value=expected_result)

        result = self.application.exception_handler(exception)

        self.assertEqual(result, expected_result)
        self.application._exception_handler.assert_called_once_with(exception)

    def test_exception_handler__not_handle(self):
        class Error(Exception):
            pass
        exception = Error()
        self.application._exception_handler = None

        self.assertRaises(Error, self.application.exception_handler, exception)

    def test_add_sensor__fresh(self):
        id_ = MagicMock()
        sensor = MagicMock()

        self.application.add_sensor(id_, sensor)

        self.assertEqual(self.application.sensors, {id_: sensor})

    def test_add_sensor__exists(self):
        id1 = MagicMock()
        id2 = MagicMock()
        sensor1 = MagicMock()
        sensor2 = MagicMock()
        self.application.sensors = {id1: sensor1}

        self.application.add_sensor(id2, sensor2)

        self.assertEqual(self.application.sensors, {id1: sensor1, id2: sensor2})

    def test_add_state__fresh(self):
        id_ = MagicMock()
        state = MagicMock()

        self.application.add_state(id_, state)

        self.assertEqual(self.application.states, {id_: state})

    def test_add_state__exists(self):
        id1 = MagicMock()
        id2 = MagicMock()
        state1 = MagicMock()
        state2 = MagicMock()
        self.application.states = {id1: state1}

        self.application.add_state(id2, state2)

        self.assertEqual(self.application.states, {id1: state1, id2: state2})

    def test_add_action_descriptor__fresh(self):
        id_ = MagicMock()
        action_descriptor = MagicMock()

        self.application.add_action_descriptor(id_, action_descriptor)

        self.assertEqual(self.application.action_descriptors, {id_: action_descriptor})

    def test_add_action_descriptor__exists(self):
        id1 = MagicMock()
        id2 = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.application.action_descriptors = {id1: action_descriptor1}

        self.application.add_action_descriptor(id2, action_descriptor2)

        self.assertEqual(self.application.action_descriptors, {id1: action_descriptor1, id2: action_descriptor2})

    def test_set_state__set_replace(self):
        old_state = MagicMock()
        old_state.deactivate = CoroutineMock()
        new_state = MagicMock()
        new_state.activate = CoroutineMock()
        new_state.reactivatable = False
        self.application.state = old_state

        self.loop.run_until_complete(self.application.set_state(new_state))

        self.assertEqual(self.application.state, new_state)
        old_state.deactivate.assert_called_once_with()
        new_state.activate.assert_called_once_with()

    def test_set_state__set_fresh(self):
        new_state = MagicMock()
        new_state.activate = CoroutineMock()
        new_state.reactivatable = False
        self.application.state = None

        self.loop.run_until_complete(self.application.set_state(new_state))

        self.assertEqual(self.application.state, new_state)
        new_state.activate.assert_called_once_with()

    def test_set_state__set_reactivatable(self):
        state = MagicMock()
        state.deactivate = CoroutineMock()
        state.activate = CoroutineMock()
        state.reactivatable = True
        self.application.state = state

        self.loop.run_until_complete(self.application.set_state(state))

        self.assertEqual(self.application.state, state)
        state.deactivate.assert_called_once_with()
        state.activate.assert_called_once_with()

    def test_set_state__ignore(self):
        state = MagicMock()
        state.activate = CoroutineMock()
        state.reactivatable = False
        self.application.state = state

        self.loop.run_until_complete(self.application.set_state(state))

        self.assertEqual(self.application.state, state)
        state.deactivate.assert_not_called()
        state.activate.assert_not_called()

    def test_run__state(self):
        sensor = MagicMock()
        sensor.run_forever = CoroutineMock()
        async def stop():
            while not self.application._app_run_future:
                await asyncio.sleep(0.1)
            self.application._app_run_future.set_result(None)
        self.application.sensors = {sensor.id: sensor}
        state = MagicMock()
        state.deactivate = CoroutineMock()
        self.application.state = state

        asyncio.ensure_future(stop())
        self.loop.run_until_complete(self.application.run())

        self.assertIsNone(self.application._app_run_future)
        for sensor in self.application.sensors.values():
            sensor.stop.assert_called_once_with()
            sensor.run_forever.assert_called_once_with()
        self.application.state.deactivate.assert_called_once_with()

    def test_run__no_state(self):
        sensor = MagicMock()
        sensor.run_forever = CoroutineMock()
        async def stop():
            while not self.application._app_run_future:
                await asyncio.sleep(0.1)
            self.application._app_run_future.set_result(None)
        self.application.sensors = {sensor.id: sensor}
        self.application.state = None

        asyncio.ensure_future(stop())
        self.loop.run_until_complete(self.application.run())

        self.assertIsNone(self.application._app_run_future)
        for sensor in self.application.sensors.values():
            sensor.stop.assert_called_once_with()
            sensor.run_forever.assert_called_once_with()

    def test_stop__running(self):
        self.application._app_run_future = asyncio.Future()

        self.application.stop()

        self.assertTrue(self.application._app_run_future.done())

    def test_stop__not_running(self):
        self.application._app_run_future = None

        self.application.stop()

    def test_notify__state(self):
        sensor = MagicMock()
        code = MagicMock()
        expected_result = MagicMock()
        state = MagicMock()
        state.notify = CoroutineMock(return_value=expected_result)
        self.application.state = state

        result = self.loop.run_until_complete(self.application.notify(sensor, code))

        self.assertEqual(result, expected_result)
        state.notify.assert_called_once_with(sensor, code)

    def test_notify__no_state(self):
        sensor = MagicMock()
        code = MagicMock()
        self.application.state = None

        result = self.loop.run_until_complete(self.application.notify(sensor, code))

        self.assertIsNone(result)
