from unittest.mock import MagicMock, patch, call

from asynctest.mock import CoroutineMock, call as async_call

from tests.common import BaseTest
from alarme.extras import RfTransmitterAction
from alarme.extras.action import rf_transmitter


class RfTransmitterActionTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.gpio = MagicMock()
        self.code = MagicMock()
        self.code_extra = MagicMock()
        self.run_count = MagicMock()
        self.run_interval = MagicMock()
        with patch.object(rf_transmitter, 'SingleRFDevice') as rf_device_mock:
            self.action = RfTransmitterAction(self.app, self.id, self.gpio, self.code, self.code_extra, self.run_count,
                                              self.run_interval)
            self.rf_device_class = rf_device_mock
            self.rf_device = self.action.rf_device

    def test_init(self):
        self.rf_device_class.assert_called_once_with(self.gpio)

    def test_run__instant_cancel(self):
        self.action._continue = MagicMock(return_value=False)

        self.loop.run_until_complete(self.action.run())

        self.action._continue.assert_called_once_with(0)
        self.rf_device.enable_tx.assert_called_once_with()
        self.rf_device.disable_tx.assert_called_once_with()
        self.rf_device.tx_code.assert_not_called()

    def test_run__sent(self):
        self.action.run_count = 3
        self.action._continue = MagicMock(side_effect=lambda x: x < self.action.run_count)

        with patch.object(rf_transmitter.asyncio, 'sleep', CoroutineMock()) as sleep_mock:
            self.loop.run_until_complete(self.action.run())

        sleep_mock.assert_has_calls([async_call(self.run_interval), async_call(self.run_interval)])
        self.rf_device.enable_tx.assert_called_once_with()
        self.rf_device.disable_tx.assert_called_once_with()
        final_code = self.code + self.code_extra
        self.rf_device.tx_code.assert_has_calls([call(final_code), call(final_code), call(final_code)])

    def test_run__cancel(self):
        self.action.run_count = 3
        self.action._continue = MagicMock(side_effect=lambda x: x < (self.action.run_count - 1))

        with patch.object(rf_transmitter.asyncio, 'sleep', CoroutineMock()) as sleep_mock:
            self.loop.run_until_complete(self.action.run())

        sleep_mock.assert_has_calls([async_call(self.run_interval)])
        self.rf_device.enable_tx.assert_called_once_with()
        self.rf_device.disable_tx.assert_called_once_with()
        final_code = self.code + self.code_extra
        self.rf_device.tx_code.assert_has_calls([call(final_code), call(final_code)])

    def test_continue__not_running(self):
        self.action.running = False
        self.action.run_count = 42

        result = self.action._continue(0)

        self.assertFalse(result)

    def test_continue__infinite_count(self):
        self.action.running = True
        self.action.run_count = None

        result = self.action._continue(42)

        self.assertTrue(result)

    def test_continue__yes(self):
        self.action.running = True
        self.action.run_count = 42

        result = self.action._continue(41)

        self.assertTrue(result)

    def test_continue__no(self):
        self.action.running = True
        self.action.run_count = 42

        result = self.action._continue(42)

        self.assertFalse(result)
