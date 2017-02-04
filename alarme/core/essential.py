import asyncio

from structlog import get_logger


class Essential:

    def __init__(self, app, id_):
        self.app = app
        self.id = id_
        self.logger = get_logger(id=self.id)
        self.loop = asyncio.get_event_loop()
