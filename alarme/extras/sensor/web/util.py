from aiohttp import BasicAuth
from aiohttp.web import HTTPUnauthorized


AUTH_REQUIRED_HEADERS = {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}


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
