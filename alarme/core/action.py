from .essential import Essential


class Action(Essential):

    def __init__(self, app, name, id_):
        super().__init__(app, name, id_)
        self.running = True

    async def run(self):
        pass

    def stop(self):
        self.logger.info('action_stop')
        self.running = False

    async def cleanup(self):
        self.logger.info('action_cleanup')
