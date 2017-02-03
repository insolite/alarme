from aiohttp.web import HTTPFound

from .core import CoreView
from ..util import login_required, handle_exception


class Home(CoreView):

    @login_required
    async def req(self):
        return HTTPFound(self.request.app.router.get('control').url())

    @handle_exception
    async def get(self):
        self.sensor.app.stop()
        return await self.req()

    @handle_exception
    async def post(self):
        return await self.req()
