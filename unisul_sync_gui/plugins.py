
from . import (
    settings, 
    builtin_plugins, 
    config,
)

import os
import sys
import platform
import importlib


def scan_modules(paths):
    for directory in paths:
        if os.path.exists(directory):
            for path in os.listdir(directory):
                full_path = os.path.join(directory, path) 
                if os.path.isfile(full_path):
                    name, ext = os.path.splitext(path)
                    if ext == '.py':
                        yield directory, name


def default_paths():
    platforms = {
        'Windows': settings.WIN_PLUGIN_PATHS
    }

    paths = platforms.get(platform.system(), 
                          settings.PLUGIN_PATHS)

    # default user configuration plugins
    paths.append(config.path_name_of('plugins'))

    return list(map(os.path.expanduser, paths))


class PluginManager:
    def __init__(self, paths: list = None):
        self.paths = paths or default_paths()
        self._objs = []
        self._sys_path = sys.path.copy()

    def register(self, *args, **kwargs):
        self.register_builtins(*args, **kwargs)
        self.register_from_paths(*args, **kwargs)

    def register_from_paths(self, *args, **kwargs):
        try:
            for directory, module_path in scan_modules(self.paths):
                # make python see our module
                sys.path.append(directory)

                module = importlib.import_module(module_path)
                self._load_module(module, *args, **kwargs)

                # restore path
                self._reset_sys_path()
        finally:
            self._reset_sys_path()

    def register_builtins(self, *args, **kwargs):
        for module in builtin_plugins.available_modules():
            self._load_module(module, *args, **kwargs)

    def _load_module(self, module, *args, **kwargs):
        result = module.plugin(*args, **kwargs)
        if result is not None:
            self._objs.append(result)
        
    def _reset_sys_path(self):
        sys.path = self._sys_path
