from . import settings

import platform
import json
import os


def load():
    if not os.path.exists(config_name()):
        os.makedirs(config_path(), mode=0o700, exist_ok=True)

        # insert the default settings
        update(settings.DEFAULT_CONFIG_SETTINGS, no_load=True)

    with open(config_name(), encoding='utf8') as io_reader:
        return json.load(io_reader)


def update(new_settings, no_load=False):
    old_settings = dict() if no_load else load()
    
    for k, v in new_settings.items():
        old_settings[k] = v

    with open(config_name(), 'w', encoding='utf8') as io_writer:
        json.dump(old_settings, io_writer, indent=4)


def config_path():
    platforms = {
        'Windows': settings.WIN_CONFIG_PATH
    }

    path = platforms.get(platform.system(), 
                         settings.CONFIG_PATH)

    return os.path.expanduser(path)


def config_name():
    return path_name_of('cfg.json')


def path_name_of(file_name):
    return os.path.join(config_path(), file_name)


def just_once(fn):
    def wrapper(*args, **kwargs):
        cfg = load()
        if cfg.get('first_time', False):
            return fn(*args, **kwargs)
    return wrapper