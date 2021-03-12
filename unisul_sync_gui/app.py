from . import config, signals, dist_util
from .crawler import auth
from PyQt5 import QtWidgets, QtGui
import requests

import functools
import sys
import os


def cached_property(getter):
    return property(functools.lru_cache()(getter))


def find_downstream_directory(name, prevpath=None):
    current_path = prevpath or '.'
    for path in next(os.walk(current_path))[1]:
        full_path = os.path.join(os.path.abspath(current_path), path)
        if os.path.basename(full_path) == name.strip('/'):
            return full_path
        result = find_downstream_directory(name, prevpath=full_path)
        if result:
            return result


def eva_icon(size: str='16x16'):
    icons_dirname = dist_util.find_icons_dirname()
    return os.path.join(icons_dirname,
                        'icons',
                        'hicolor',
                        size, 
                        'apps', 
                        'eva.png')


async def create_auth_manager(auto=True, 
                              remember_me=False) -> auth.AsyncAuthManager:
    '''
    Handle creating the authentication manager class. It may
    try to call automatic authentication.

    If ``auto`` is true automatic login from file credentials.
    
    It will always try to authentication with the current cookies.  
    '''

    auth_manager = auth.AsyncAuthManager(
        config.creds_name(),
        config.cookies_name(),
    )

    # simulate a "async with" to load cookies
    await auth_manager.__aenter__()

    if auto:
        # try from cookies
        await auth_manager.from_cookies()
        
        # maybe try from credentials when cookies failed
        if remember_me and not auth_manager.is_logged_in:
            await auth_manager.from_rememberme()

    return auth_manager


class AppCtxt:
    def __init__(self):
        self._clear_config()
        self.windows = {}
        self.app.setWindowIcon(QtGui.QIcon(eva_icon('128x128')))

    @cached_property
    def app(self):
        return QtWidgets.QApplication([])

    @cached_property
    def signals(self):
        return signals._signals()

    @property
    def config(self):
        if self._config is None:
            self._config = config.load()
        return self._config

    @cached_property
    def http_session(self):
        return requests.Session()

    @cached_property
    def book_bot_path(self):
        return find_downstream_directory('book_bot')

    def update_config(self, new_settings):
        config.update(new_settings)
        self._clear_config()

    def fix_config(self, default_settings):
        config.fix_config(default_settings)
        self._clear_config()

    def exit(self, returncode = 0):
        self.windows = {}
        sys.exit(returncode)

    def _clear_config(self):
        self._config = None


context = AppCtxt()