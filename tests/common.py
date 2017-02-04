import asyncio
from unittest import TestCase


class BaseTest(TestCase):

    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
