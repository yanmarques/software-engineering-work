from . import config, signals
from PyQt5.QtWidgets import QApplication

import requests
import functools
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


class AppCtxt:
    def __init__(self):
        self._clear_config()
        self.windows = {}
        self.app

    @cached_property
    def app(self):
        return QApplication([])

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

    def _clear_config(self):
        self._config = None


context = AppCtxt()