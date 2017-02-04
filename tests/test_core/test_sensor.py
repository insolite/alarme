import asyncio
from unittest.mock import MagicMock

from asynctest import CoroutineMock

from alarme import Sensor
from tests.common import BaseTest


class SensorTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.sensor = Sensor(self.app, self.id)

    def test_add_behaviour__fresh(self):
        code = MagicMock()
        action_descriptor = MagicMock()

        self.sensor.add_behaviour(code, action_descriptor)

        self.assertEqual(self.sensor.behaviours, {code: [action_descriptor]})

    def test_add_behaviour__same_code_exists(self):
        code = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.sensor.behaviours = {code: [action_descriptor1]}

        self.sensor.add_behaviour(code, action_descriptor2)

        self.assertEqual(self.sensor.behaviours, {code: [action_descriptor1, action_descriptor2]})

    def test_add_behaviour__another_code_exists(self):
        code1 = MagicMock()
        code2 = MagicMock()
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.sensor.behaviours = {code1: [action_descriptor1]}

        self.sensor.add_behaviour(code2, action_descriptor2)

        self.assertEqual(self.sensor.behaviours, {code1: [action_descriptor1], code2: [action_descriptor2]})

    def test_run_forever__end(self):
        def stop():
            self.sensor.running = False
        self.sensor.run = CoroutineMock(side_effect=stop)
        self.sensor.cleanup = CoroutineMock()

        self.loop.run_until_complete(self.sensor.run_forever())

        self.sensor.cleanup.assert_called_once_with()

    def test_run_forever__crash(self):
        class Error(Exception):
            pass
        def stop():
            self.sensor.running = False
            raise Error
        self.sensor.run = CoroutineMock(side_effect=stop)
        self.sensor.cleanup = CoroutineMock()

        self.loop.run_until_complete(self.sensor.run_forever())

        self.sensor.cleanup.assert_called_once_with()

    def test_run(self):
        future = asyncio.ensure_future(self.sensor.run())
        self.loop.run_until_complete(asyncio.sleep(0.5))
        self.sensor.running = False
        self.loop.run_until_complete(asyncio.wait_for(future, 0.5))

    def test_stop(self):
        self.sensor.running = True

        self.sensor.stop()

        self.assertFalse(self.sensor.running)

    def test_cleanup(self):
        self.loop.run_until_complete(self.sensor.cleanup())

    def test_notify(self):
        code = MagicMock()
        self.app.notify = CoroutineMock()

        self.loop.run_until_complete(self.sensor.notify(code))

        self.app.notify.assert_called_once_with(self.sensor, code)
