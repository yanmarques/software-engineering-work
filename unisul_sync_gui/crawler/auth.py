from . import abc, json, EVA_DOMAIN

from urllib.parse import urljoin


class _names:
    username = 'id_login'
    password = 'id_senha'


class NotAuthenticatedException(Exception):
    def __init__(self, message='User is not authenticated.', **kwargs):
        super().__init__(message, **kwargs)


class AsyncAuthManager:
    def __init__(self):
        '''
        Provides an interface to Eva web authentication
        mechanism.
        '''

        self._logged = False

    @property
    def is_logged_in(self):
        return self._logged

    def from_cookies(self) -> bool:
        '''
        Try to authenticate using any existing cookies.
        Returns whether it succeeded.
        '''

        pass

    def from_creds(self, 
                   username, 
                   password, 
                   rememberme=False) -> bool:
        '''
        Try to authenticate using given credentials.
        Returns whether it succeeded.

        If ``rememberme`` is true, save credentials on disk.
        '''

        pass

    def from_rememberme(self) -> bool:
        '''
        Try to authenticate using credentials stored in a 
        configuration file.
        Returns whether it succeeded.
        '''

        pass

    def logout(self):
        '''
        When logged in, try to deactivate the cookies sending a logout
        reques to server.
        '''

        pass
