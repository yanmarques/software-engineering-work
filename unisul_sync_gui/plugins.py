
from . import settings, builtin_plugins, config

import os
import sys
import platform
import importlib


def scan_modules():
    for directory in default_paths():
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

    paths.append(config.path_name_of('plugins'))

    return list(map(os.path.expanduser, paths))


def maybe_call(obj, fn_name, *args, **kwargs):
    if hasattr(obj, fn_name):
        result = getattr(obj, fn_name)(*args, **kwargs)
        return (result)


class PluginManager:
    def __init__(self):
        self.objs = []
        self._register_modules()

    def _register_modules(self, *args, **kwargs):
        for module in builtin_plugins.available_modules():
            klass = module.plugin(*args, **kwargs)
            self.objs.append(klass)

        source_path = sys.path.copy() 

        try:
            for directory, module_path in scan_modules():
                # make python see our module
                sys.path.append(directory)

                module = importlib.import_module(module_path)
                klass = module.plugin(*args, **kwargs)
                self.objs.append(klass)

                # restore path
                sys.path = source_path
        finally:
            sys.path = source_path
