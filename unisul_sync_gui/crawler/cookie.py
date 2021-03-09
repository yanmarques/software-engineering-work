from ..config import path_name_of
from aiohttp import ClientSession as _ClientSession

import os


class ClientSession(_ClientSession):
    '''
    Automatically loads and saves the cookie from/to disk.
    '''

    async def __aenter__(self) -> "ClientSession":
        if os.path.exists(cookie_name()):
            self.cookie_jar.load(cookie_name())

        return await super().__aenter__()

    def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cookie_jar.save(cookie_name())
        return super().__aexit__(exc_type, exc_val, exc_tb)


def cookie_name():
    '''
    Path of http cookie files.
    '''

    return path_name_of('cookies')