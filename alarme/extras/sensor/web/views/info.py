import alarme

from .core import CoreView
from ..util import login_required, handle_exception, json_response, expand_color


class Info(CoreView):

    @handle_exception
    @login_required
    @json_response
    async def get(self):
        states = self.sensor.app.states
        buttons = self.sensor.buttons.copy()
        for button in buttons.values():
            button['color'] = expand_color(button['color'], states)
        # TODO: add behaviours to response
        return {'app': {'version': alarme.__version__},
                'current_state': self.sensor.app.state.as_dict(),
                'buttons': buttons,
                'states': {state.id: state.as_dict()
                           for state in states.values()}}
