from ..config import path_name_of
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

        return await super().__aenter__()

    def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cookie_jar.save(self.cookies_path)
        return super().__aexit__(exc_type, exc_val, exc_tb)
