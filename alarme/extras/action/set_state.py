import asyncio

from alarme import Action


class SetStateAction(Action):

    def __init__(self, app, id_, state_id):
        super().__init__(app, id_)
        self.state_id = state_id

    async def run(self):
        # Can't await cause this action must end in current state deactivation, so asyncio.ensure_future
        return asyncio.ensure_future(self.app.set_state(self.app.states[self.state_id]))
