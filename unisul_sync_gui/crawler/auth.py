import aiohttp
from . import (
    json, 
    cookie,
    EVA_DOMAIN,
)
from .. import config

import os
from urllib.parse import urljoin


class NotAuthenticatedException(Exception):
    def __init__(self, message='User is not authenticated.', **kwargs):
        super().__init__(message, **kwargs)


class AsyncAuthManager:
    user_field = 'id_login'
    passwd_field = 'id_senha'

    def __init__(self):
        '''
        Provides an interface to Eva web authentication
        mechanism.
        '''

        self._logged = False
        self._session = cookie.ClientSession()
        self._dumper = json.JsonDumper(auth_name())

    @property
    def is_logged_in(self):
        '''
        Returns whether session is authenticated.
        '''

        return self._logged

    async def __aenter__(self) -> "AsyncAuthManager":
        return await self._session.__aenter__()

    def __aexit__(self, *args):
        return self._session.__aexit__(*args)

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
            self._dumper.dump(data)
            os.chmod(auth_name(), 0o600)

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

        # check for form fields
        has_fields = self.user_field in body and self.passwd_field in body

        # check for redirect url
        has_js_redirect = 'eadv4/login/index.jsp' in body

        return not (has_fields or has_js_redirect)

    def load_creds(self):
        '''
        Return a tuple with username and password respectively.

        If file is missing or disk credentials have missing
        parameters, None is returned.
        '''

        if not os.path.exists(auth_name()):
            return

        auth_data = self._dumper.load()
        
        credentials = (auth_data.get(self.user_field), 
                       auth_data.get(self.passwd_field))

        if all(credentials):
            return credentials

    async def _remember_auth_response(self, *args, **kwargs):
        '''
        Make a request and record whether is authenticated.
        '''

        async with self._session.request(*args, **kwargs) as resp:
            result = await self.check_response(resp)
        
        return self._set_logged(result)

    def _request(self, method, path, **kwargs):
        '''
        Open a http request using underlying session.
        '''

        url = urljoin(f'https://{EVA_DOMAIN}', path)

        return self._session.request(method, url, **kwargs)


def auth_name():
    return config.path_name_of('auth.json')