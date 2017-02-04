from .essential import Essential


class Action(Essential):

    def __init__(self, app, name, id_):
        super().__init__(app, name, id_)
        self.running = True

    async def execute(self):
        self.logger.info('action_run')
        try:
            await self.run()
        except:
            self.logger.error('action_crash', exc_info=True)
            raise
        else:
            self.logger.info('action_end')
        finally:
            await self.cleanup()

    async def run(self):
        pass

    def stop(self):
        self.logger.info('action_stop')
        self.running = False

    async def cleanup(self):
        self.logger.info('action_cleanup')
