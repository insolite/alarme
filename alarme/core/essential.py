import asyncio

from structlog import get_logger


class Essential:

    def __init__(self, app, name, id_):
        self.app = app
        self.name = name
        self.id = id_
        self.logger = get_logger(name=self.name)
        self.loop = asyncio.get_event_loop()
