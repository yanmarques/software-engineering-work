import asyncio
import aiohttp
from aiohttp.client import ClientSession
from . import (
    json, 
    cookie,
    EVA_DOMAIN,
)
from ..util import logger

import os
from urllib.parse import urljoin


class NotAuthenticatedException(Exception):
    def __init__(self, message='User is not authenticated.', **kwargs):
        super().__init__(message, **kwargs)


class AsyncAuthManager:
    user_field = 'id_login'
    passwd_field = 'id_senha'

    def __init__(self, 
                 creds_path: str,
                 session: ClientSession = None):
        '''
        Provides an interface to Eva web authentication
        mechanism.

        cookies_path: File location to save the cookies.
        '''

        self._logged = False
        self._creds = json.JsonDumper(creds_path)
        self._session = session or ClientSession()

    @property
    def is_logged_in(self):
        '''
        Returns whether session is authenticated.
        '''

        return self._logged

    async def __aenter__(self) -> "AsyncAuthManager":
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()
        return await self._session.__aexit__(*args)

    async def close(self):
        '''
        Close underlying web client session.
        '''

        await self._session.close()

    async def from_cookies(self) -> bool:
        '''
        Try to authenticate using any existing cookies.
        Returns whether it succeeded.
        '''

        return await self._remember_auth_response('GET', '/')

    async def from_creds(self, 
                         username, 
                         password, 
                         rememberme=False) -> bool:
        '''
        Try to authenticate using given credentials.
        Returns whether it succeeded.

        If ``rememberme`` is true, save credentials on disk.
        '''

        data = {self.user_field: username, 
                self.passwd_field: password}

        await self._remember_auth_response('POST', 
                                           '/login.processa', 
                                           data=data)

        # handle saving credentials file
        if rememberme and self.is_logged_in:
            # send to disk
            self._creds.dump(data)
            self.set_creds_perms()

        return self.is_logged_in


    async def from_rememberme(self) -> bool:
        '''
        Try to authenticate using credentials stored in a 
        configuration file.
        Returns whether it succeeded.
        '''

        creds = self.load_creds()

        # any creds available
        if creds is None:
            return self.is_logged_in

        return await self.from_creds(*creds)

    def logout(self):
        '''
        When logged in, try to deactivate the cookies sending a logout
        reques to server.
        '''

        pass

    async def check_response(self, response: aiohttp.ClientResponse):
        '''
        Returns whether the response is not unauthenticated.
        '''

        if response.history and response.history[-1].status != 302:
            return True

        # read response body
        body = await response.text()

        # check for redirect url
        has_js_redirect = 'eadv4/login/index.jsp' in body

        return not has_js_redirect

    def load_creds(self):
        '''
        Return a tuple with username and password respectively.

        If file is missing or disk credentials have missing
        parameters, None is returned.
        '''

        if not os.path.exists(self._creds.path):
            return

        # fix file permissions
        self.set_creds_perms()

        auth_data = self._creds.load()
        
        # creates (username, password) tuple
        credentials = (auth_data.get(self.user_field), 
                       auth_data.get(self.passwd_field))

        if all(credentials):
            return credentials

    def set_creds_perms(self):
        '''
        Restrict access of credentials file to owner-only.
        '''

        os.chmod(self._creds.path, 0o600)

    async def _remember_auth_response(self, *args, **kwargs):
        '''
        Make a request and record whether is authenticated.
        '''

        async with self._request(*args, **kwargs) as resp:
            self._logged = await self.check_response(resp)
        
        return self.is_logged_in

    def _request(self, method, path, **kwargs):
        '''
        Open a http request using underlying session.
        '''

        url = urljoin(f'https://{EVA_DOMAIN}', path)

        return self._session.request(method, url, **kwargs)
