import asyncio
from functools import partial

from aiotg import Bot

from alarme import Sensor


class TelegramSensor(Sensor):

    def __init__(self, app, id_, api_token, commands={}):
        super().__init__(app, id_)
        self.api_token = api_token
        self.bot = Bot(api_token=api_token)
        for command in commands.values():
            self.bot.add_command(command['regexp'], asyncio.coroutine(partial(self.handle_command, command)))
        self.loop_task = None

    async def handle_command(self, command, chat, match):
        env = {
            'current_state_id': self.app.state.id if self.app.state else None
        }
        env.update(match.groupdict())
        behaviour = command.get('behaviour')
        if behaviour:
            futures = await self.notify(behaviour.format(**env))
            for future in (futures or []):
                await future
        reply = command.get('reply')
        if reply is not None:
            await chat.send_text(reply.format(**env))

    async def run(self):
        self.loop_task = asyncio.ensure_future(self.bot.loop())
        await super().run()

    async def cleanup(self):
        await super().cleanup()
        if self.loop_task:
            self.loop_task.cancel()
