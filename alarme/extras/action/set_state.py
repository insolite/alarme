import os
import asyncio

from alarme import Action


class SetStateAction(Action):

    def __init__(self, app, id_, state_id, last_state_file=None, fallback_state_id=None):
        super().__init__(app, id_)
        self.state_id = state_id
        self.last_state_file = last_state_file
        self.fallback_state_id = fallback_state_id

    async def run(self):
        state_id = self.state_id
        if not state_id:
            state_id = self.read_last_state()
            if not state_id or self.app.state and self.app.state.id == state_id:
                state_id = self.fallback_state_id
        state = self.app.states[state_id]
        self.write_last_state(state)
        # Can't await cause this action must end in current state deactivation, so asyncio.ensure_future
        return asyncio.ensure_future(self.app.set_state(state))

    def read_last_state(self):
        if self.last_state_file:
            try:
                with open(self.last_state_file, 'r') as f:
                    return f.read().strip()
            except:
                self.logger.error('last_state_file_read_error', filename=self.last_state_file)

    def write_last_state(self, state):
        if self.last_state_file:
            try:
                dirname = os.path.dirname(self.last_state_file)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                with open(self.last_state_file, 'w') as f:
                    f.write(state.id)
                return True
            except:
                self.logger.error('last_state_file_write_error', last_state_file=self.last_state_file, state=state)
                return False
