import json

from aiohttp import BasicAuth
from aiohttp.web import HTTPUnauthorized, Response


AUTH_REQUIRED_HEADERS = {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}
STATE_COLOR_PREFIX = '@'


def login_required(func):
    async def wrapped(self, *args, **kwargs):
        if (self.sensor.login, self.sensor.password) == (None, None):
            return await func(self, *args, **kwargs)
        auth_header = self.request.headers.get('Authorization')
        if auth_header:
            auth = BasicAuth.decode(auth_header)
            if (auth.login, auth.password) == (self.sensor.login, self.sensor.password):
                return await func(self, *args, **kwargs)
        return HTTPUnauthorized(headers=AUTH_REQUIRED_HEADERS)
    return wrapped


def handle_exception(func):
    async def wrapped(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as err:
            self.sensor.app.exception_handler(err)
            raise
    return wrapped


def json_response(func):
    async def wrapped(self, *args, **kwargs):
        return Response(text=json.dumps(await func(self, *args, **kwargs)), content_type='text/json')
    return wrapped


def expand_color(color, states):
    if color.strip().startswith(STATE_COLOR_PREFIX):
        return states[color.replace(STATE_COLOR_PREFIX, '')].color
    return color
