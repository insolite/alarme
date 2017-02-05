import asyncio
from unittest.mock import MagicMock, call
from functools import partial

from asynctest import CoroutineMock

from alarme import Schedule
from alarme.core.schedule import ScheduleStop
from tests.common import BaseTest


class ScheduleTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.state = MagicMock()
        self.Schedule = partial(Schedule, self.app, self.id, self.state)
        self.schedule = self.Schedule()

    def test_add_action__fresh(self):
        action_descriptor = MagicMock()

        self.schedule.add_action(action_descriptor)

        self.assertEqual(self.schedule.actions, [action_descriptor])

    def test_add_action__exists(self):
        action_descriptor1 = MagicMock()
        action_descriptor2 = MagicMock()
        self.schedule.actions = [action_descriptor1]

        self.schedule.add_action(action_descriptor2)

        self.assertEqual(self.schedule.actions, [action_descriptor1, action_descriptor2])

    def test_end(self):
        self.schedule._future = MagicMock()

        self.assertRaises(ScheduleStop, self.schedule._end)

        self.assertIsNone(self.schedule._future)

    def test_end_sleep__new(self):
        self.schedule._future = asyncio.Future()

        self.schedule._end_sleep()

        self.assertTrue(self.schedule._future.done())

    def test_end_sleep__already_done(self):
        self.schedule._future = asyncio.Future()
        self.schedule._future.set_result(None)

        self.schedule._end_sleep()

        self.assertTrue(self.schedule._future.done())

    def test_sleep__end(self):
        delay = 0.1
        self.schedule._end = MagicMock(side_effect=ScheduleStop)
        self.schedule._end_sleep = MagicMock()
        self.schedule.running = False

        self.assertRaises(ScheduleStop, self.loop.run_until_complete, self.schedule._sleep(delay))

        self.schedule._end.assert_called_once_with()
        self.schedule._end_sleep.assert_not_called()

    def test_sleep__fine(self):
        delay = 0.1
        def end_sleep():
            self.schedule._future.set_result(None)
        self.schedule._end = MagicMock()
        self.schedule._end_sleep = MagicMock(side_effect=end_sleep)
        self.schedule.running = True

        self.loop.run_until_complete(self.schedule._sleep(delay))

        self.schedule._end.assert_not_called()
        self.schedule._end_sleep.assert_called_once_with()

    def test_sleep__cancel(self):
        delay = 0.1
        def end_sleep():
            self.schedule._future.cancel()
        self.schedule._end = MagicMock()
        self.schedule._end_sleep = MagicMock(side_effect=end_sleep)
        self.schedule.running = True

        self.loop.run_until_complete(self.schedule._sleep(delay))

        self.schedule._end.assert_called_once_with()
        self.schedule._end_sleep.assert_called_once_with()

    def test_continue__true_1(self):
        self.schedule.running = True
        self.schedule.run_count = None
        run_count = 42
        expected_result = True

        result = self.schedule._continue(run_count)

        self.assertEqual(result, expected_result)

    def test_continue__true_2(self):
        self.schedule.running = True
        self.schedule.run_count = 43
        run_count = 42
        expected_result = True

        result = self.schedule._continue(run_count)

        self.assertEqual(result, expected_result)

    def test_continue__false_1(self):
        self.schedule.running = True
        self.schedule.run_count = 42
        run_count = 42
        expected_result = False

        result = self.schedule._continue(run_count)

        self.assertEqual(result, expected_result)

    def test_continue__false_2(self):
        self.schedule.running = False
        self.schedule.run_count = 43
        run_count = 42
        expected_result = False

        result = self.schedule._continue(run_count)

        self.assertEqual(result, expected_result)

    def test_continue__false_3(self):
        self.schedule.running = False
        self.schedule.run_count = None
        run_count = 42
        expected_result = False

        result = self.schedule._continue(run_count)

        self.assertEqual(result, expected_result)

    def test_run_actions__all(self):
        self.schedule.running = True
        action1 = MagicMock()
        action1.execute = CoroutineMock()
        action_descriptor1 = MagicMock()
        action_descriptor1.construct = MagicMock(return_value=action1)
        action2 = MagicMock()
        action2.execute = CoroutineMock()
        action_descriptor2 = MagicMock()
        action_descriptor2.construct = MagicMock(return_value=action2)
        self.schedule.actions = [action_descriptor1, action_descriptor2]

        self.loop.run_until_complete(self.schedule.run_actions())

        self.assertIsNone(self.schedule.active_action)
        action_descriptor1.construct.assert_called_once_with()
        action1.execute.assert_called_once_with()
        action_descriptor2.construct.assert_called_once_with()
        action2.execute.assert_called_once_with()

    def test_run_actions__action_crash(self):
        self.schedule.running = True
        action1 = MagicMock()
        action1.execute = CoroutineMock(side_effect=[Exception, None])
        action_descriptor1 = MagicMock()
        action_descriptor1.construct = MagicMock(return_value=action1)
        action2 = MagicMock()
        action2.execute = CoroutineMock()
        action_descriptor2 = MagicMock()
        action_descriptor2.construct = MagicMock(return_value=action2)
        self.schedule.actions = [action_descriptor1, action_descriptor2]

        self.loop.run_until_complete(self.schedule.run_actions())

        self.assertIsNone(self.schedule.active_action)
        action_descriptor1.construct.assert_called_once_with()
        action1.execute.assert_has_calls([call(), call()])
        action_descriptor2.construct.assert_called_once_with()
        action2.execute.assert_called_once_with()

    def test_run_actions__cancel(self):
        self.schedule.running = True
        def stop():
            self.schedule.running = False
        action1 = MagicMock()
        action1.execute = CoroutineMock(side_effect=stop)
        action_descriptor1 = MagicMock()
        action_descriptor1.construct = MagicMock(return_value=action1)
        action2 = MagicMock()
        action2.execute = CoroutineMock()
        action_descriptor2 = MagicMock()
        action_descriptor2.construct = MagicMock(return_value=action2)
        self.schedule.actions = [action_descriptor1, action_descriptor2]

        self.loop.run_until_complete(self.schedule.run_actions())

        self.assertIsNone(self.schedule.active_action)
        action_descriptor1.construct.assert_called_once_with()
        action1.execute.assert_called_once_with()
        action_descriptor2.construct.assert_not_called()
        action2.execute.assert_not_called()

    def test_run__end_1(self):
        self.schedule.running = MagicMock()
        self.schedule._sleep = CoroutineMock()
        self.schedule._continue = MagicMock(side_effect=lambda x: x < 1)
        self.schedule._end = MagicMock()
        self.schedule.run_actions = CoroutineMock()

        self.loop.run_until_complete(self.schedule.run())

        self.assertFalse(self.schedule.running)
        self.schedule._sleep.assert_has_calls([call(self.schedule.delay)])
        self.schedule._continue.assert_has_calls([call(0), call(1)])
        self.schedule._end.assert_called_once_with()
        self.schedule.run_actions.assert_has_calls([call()])

    def test_run__end_2(self):
        self.schedule.running = MagicMock()
        self.schedule._sleep = CoroutineMock()
        self.schedule._continue = MagicMock(side_effect=lambda x: x < 2)
        self.schedule._end = MagicMock()
        self.schedule.run_actions = CoroutineMock()

        self.loop.run_until_complete(self.schedule.run())

        self.assertFalse(self.schedule.running)
        self.schedule._sleep.assert_has_calls([call(self.schedule.delay), call(self.schedule.run_interval)])
        self.schedule._continue.assert_has_calls([call(0), call(1), call(1)])
        self.schedule._end.assert_called_once_with()
        self.schedule.run_actions.assert_has_calls([call(), call()])

    def test_run__cancel_delay(self):
        self.schedule.running = MagicMock()
        self.schedule._sleep = CoroutineMock(side_effect=[ScheduleStop])
        self.schedule._continue = MagicMock(side_effect=lambda x: x < 2)
        self.schedule._end = MagicMock()
        self.schedule.run_actions = CoroutineMock()

        self.loop.run_until_complete(self.schedule.run())

        self.assertFalse(self.schedule.running)
        self.schedule._sleep.assert_has_calls([call(self.schedule.delay)])
        self.schedule._continue.assert_not_called()
        self.schedule._end.assert_not_called()
        self.schedule.run_actions.assert_not_called()

    def test_run__cancel_interval(self):
        self.schedule.running = MagicMock()
        self.schedule._sleep = CoroutineMock(side_effect=[None, ScheduleStop])
        self.schedule._continue = MagicMock(side_effect=lambda x: x < 2)
        self.schedule._end = MagicMock()
        self.schedule.run_actions = CoroutineMock()

        self.loop.run_until_complete(self.schedule.run())

        self.assertFalse(self.schedule.running)
        self.schedule._sleep.assert_has_calls([call(self.schedule.delay), call(self.schedule.run_interval)])
        self.schedule._continue.assert_has_calls([call(0), call(1)])
        self.schedule._end.assert_not_called()
        self.schedule.run_actions.assert_has_calls([call()])

    def test_stop__full(self):
        self.schedule.running = True
        self.schedule._future = asyncio.Future()
        self.schedule._sleep_future = asyncio.Future()
        self.schedule.active_action = MagicMock()

        self.schedule.stop()

        self.assertFalse(self.schedule.running)
        self.assertTrue(self.schedule._future.cancelled())
        self.assertTrue(self.schedule._sleep_future.cancelled())
        self.schedule.active_action.stop.assert_called_once_with()

    def test_stop__none(self):
        self.schedule.running = True
        self.schedule._future = None
        self.schedule._sleep_future = None
        self.schedule.active_action = None

        self.schedule.stop()

        self.assertFalse(self.schedule.running)
