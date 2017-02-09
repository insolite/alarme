from aiohttp_jinja2 import template

from .core import CoreView, http_found
from ..util import login_required, handle_exception


class Control(CoreView):

    @handle_exception
    @login_required
    @template('control.html')
    async def get(self):
        self.logger.debug('control_page_view')
        return {'current_state': self.sensor.app.state,
                'buttons': self.sensor.buttons,
                'states': self.sensor.app.states}

    @handle_exception
    @login_required
    @http_found
    async def post(self):
        data = await self.request.post()
        behaviour = data['behaviour']
        futures = await self.sensor.notify(behaviour)
        for future in (futures or []):
            await future
