from aiotg import Bot

from alarme import Action


class TelegramAction(Action):

    def __init__(self, app, id_, api_token, text, target):
        super().__init__(app, id_)
        self.api_token = api_token
        self.text = text
        self.target = target
        self.bot = Bot(api_token=api_token)

    async def run(self):
        chat = self.bot.private(str(self.target))
        await chat.send_text(self.text)
