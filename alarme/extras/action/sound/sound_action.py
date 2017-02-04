import sys
import asyncio
import os.path

import pyglet

from alarme import Action


class SoundAction(Action):

    def __init__(self, app, id_, sound):
        super().__init__(app, id_)
        self.sound = sound
        self._future = None

    async def run(self):
        self.logger.info('play_sound')
        package_name = sys.modules[__name__].__package__
        package_path, = sys.modules[package_name].__path__
        player = pyglet.media.Player()
        source = pyglet.media.load(os.path.join(package_path, 'sounds', self.sound), streaming=False)
        # player.push_handlers(on_eos=self.end) # Not working, so do it using call_later() and source.duration
        end_task = self.loop.call_later(source.duration, self.end)
        player.queue(source)
        player.play()
        self._future = asyncio.Future()
        await self._future
        end_task.cancel()
        player.pause()

    def end(self):
        if self._future and not self._future.done():
            self._future.set_result(None)

    def stop(self):
        super().stop()
        self.end()
