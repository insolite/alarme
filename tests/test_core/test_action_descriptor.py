from unittest.mock import MagicMock

from alarme import ActionDescriptor
from tests.common import BaseTest


class ScheduleTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.app = MagicMock()
        self.id = MagicMock()
        self.action = MagicMock()
        self.factory = MagicMock(return_value=self.action)
        self.kwargs = {'foo': 42, 'bar': 24}
        self.acrion_descriptor = ActionDescriptor(self.app, self.id, self.factory, **self.kwargs)

    def test_construct(self):
        kwargs = {'bar': 100}
        final_kwargs = self.kwargs.copy()
        final_kwargs.update(**kwargs)

        result = self.acrion_descriptor.construct(**kwargs)

        self.assertEqual(result, self.action)
        self.factory.assert_called_once_with(self.app, self.id, **final_kwargs)

    def test_clone(self):
        kwargs = {'bar': 100}
        final_kwargs = self.kwargs.copy()
        final_kwargs.update(**kwargs)

        result = self.acrion_descriptor.clone(**kwargs)

        self.assertIsInstance(result, self.acrion_descriptor.__class__)
        self.assertEqual(result.app, self.app)
        self.assertEqual(result.id, self.id)
        self.assertEqual(result.factory, self.factory)
        self.assertEqual(result.kwargs, final_kwargs)
