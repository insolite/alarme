from aiohttp_jinja2 import template

from .core import CoreView, http_found
from ..util import login_required, handle_exception


class Control(CoreView):

    @login_required
    @template('control.html')
    @handle_exception
    async def get(self):
        self.logger.debug('control_page_view')
        return {'current_state': self.sensor.app.state,
                'states': self.sensor.app.states,
                'behaviours': sorted(self.sensor.behaviours.items(), key=lambda x: x[0])}

    @login_required
    @http_found
    @handle_exception
    async def post(self):
        data = await self.request.post()
        behaviour = data['behaviour']
        await self.sensor.notify(behaviour)
