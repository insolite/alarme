from unittest.mock import MagicMock

from asynctest import CoroutineMock

from alarme import Action
from tests.common import BaseTest


class ActionTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.action = Action(self.app, self.id)

    def test_execute__end(self):
        expected_result = MagicMock()
        self.action.run = CoroutineMock(return_value=expected_result)
        self.action.cleanup = CoroutineMock()

        result = self.loop.run_until_complete(self.action.execute())

        self.action.run.assert_called_once_with()
        self.action.cleanup.assert_called_once_with()
        self.assertEqual(result, expected_result)

    def test_execute__crash(self):
        class Error(Exception):
            pass
        self.action.run = CoroutineMock(side_effect=Error)
        self.action.cleanup = CoroutineMock()

        self.assertRaises(Error, self.loop.run_until_complete, self.action.execute())

        self.action.run.assert_called_once_with()
        self.action.cleanup.assert_called_once_with()

    def test_run(self):
        self.loop.run_until_complete(self.action.run())

    def test_stop(self):
        self.action.running = True

        self.action.stop()

        self.assertFalse(self.action.running)

    def test_cleanup(self):
        self.loop.run_until_complete(self.action.cleanup())
