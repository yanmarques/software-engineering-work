from aiohttp.cookiejar import CookieJar
from aiohttp import ClientSession as _ClientSession

import os


class ClientSession(_ClientSession):
    def __init__(self, cookies_path: str, *args, **kwargs):
        '''
        Automatically loads and saves the cookie from/to disk.
        '''

        super().__init__(*args, **kwargs)
        self.cookies_path = cookies_path

    async def __aenter__(self) -> "ClientSession":
        if os.path.exists(self.cookies_path):
            self.cookie_jar.load(self.cookies_path)
            self._maybe_discard_cookie_jar()

        return await super().__aenter__()

    def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cookie_jar.save(self.cookies_path)
        return super().__aexit__(exc_type, exc_val, exc_tb)

    def _maybe_discard_cookie_jar(self):
        try:
            list(self.cookie_jar)
        except AttributeError:
            # something gone wrong when loading cookie jar
            # from disk, so discard and get a new one
            self._cookie_jar = CookieJar(loop=self.loop)
