import os.path
import sys
from functools import partial

import aiohttp_jinja2
import jinja2
from aiohttp import web

from alarme import Sensor
from . import views, filters


def generate_core_view(sensor, original_handler):
    # Can't use lambda like this, getting AttributeError:
    # return lambda x: original_handler(x)
    # AttributeError: 'RequestHandler' object has no attribute '_middlewares'
    # Probably it is an aiohttp bug
    # TODO: Check it later / post bug report
    return type(original_handler.__name__, (original_handler,),
                {'sensor': sensor})


class WebSensor(Sensor):

    def __init__(self, app, id_, host, port, buttons=[], login=None, password=None, debug=False):
        super().__init__(app, id_)
        self.host = host
        self.port = port
        self.buttons = buttons
        self.login = login
        self.password = password
        generate_view = partial(generate_core_view, self)
        app = web.Application(debug=debug)
        package_name = sys.modules[__name__].__package__
        package_path, = sys.modules[package_name].__path__
        jinja_env = aiohttp_jinja2.setup(
            app, loader=jinja2.PackageLoader(package_name))
        filter_functions = [
            filters.expand_color,
        ]
        jinja_env.filters.update({filter_function.__name__: filter_function
                                  for filter_function in filter_functions})
        app.router.add_route('*', '/control', generate_view(views.Control), name='control')
        app.router.add_route('*', '/info', generate_view(views.Info), name='info')
        app.router.add_route('*', '/', generate_view(views.Home), name='home')
        app.router.add_static('/static', path=os.path.join(package_path, 'static'), name='static')
        self.web_handler = app.make_handler()
        self.serv = None
        self.web_app = app

    async def run(self):
        self.serv = await self.loop.create_server(self.web_handler, self.host, self.port)
        await super().run()

    async def cleanup(self):
        await super().cleanup()
        self.serv.close()
        if self.serv:
            await self.serv.wait_closed()
        await self.web_app.shutdown()
        await self.web_handler.finish_connections(3)
        await self.web_app.cleanup()
