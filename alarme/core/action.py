from .essential import Essential


class Action(Essential):

    def __init__(self, app, id_):
        super().__init__(app, id_)
        self.running = True

    async def execute(self):
        self.logger.info('action_run')
        try:
            result = await self.run()
        except:
            self.logger.error('action_crash', exc_info=True)
            raise
        else:
            self.logger.info('action_end')
        finally:
            await self.cleanup()
        return result

    async def run(self):
        pass

    def stop(self):
        self.logger.info('action_stop')
        self.running = False

    async def cleanup(self):
        self.logger.info('action_cleanup')
