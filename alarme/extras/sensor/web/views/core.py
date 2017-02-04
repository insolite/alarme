from aiohttp.web import View, HTTPFound


def http_found(func):
    async def wrapped(self, *args, **kwargs):
        await func(self, *args, **kwargs)
        return HTTPFound(self.request.rel_url)
    return wrapped


class CoreView(View):

    sensor = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.sensor.logger
