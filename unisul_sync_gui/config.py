from . import settings

import platform
import json
import os


def load(no_fixing=False):
    if not os.path.exists(config_name()):
        os.makedirs(config_path(), mode=0o700, exist_ok=True)

        # insert the default settings
        update(settings.DEFAULT_CONFIG_SETTINGS, old_settings={})
    elif not no_fixing:
        old_settings = load(no_fixing=True)
        fix_config(settings.DEFAULT_CONFIG_SETTINGS, 
                   old_settings=old_settings)

    with open(config_name(), encoding='utf8') as io_reader:
        return json.load(io_reader)


def update(new_settings, old_settings=None):
    old_settings = old_settings or load()
    
    for k, v in new_settings.items():
        old_settings[k] = v

    with open(config_name(), 'w', encoding='utf8') as io_writer:
        json.dump(old_settings, io_writer, indent=4)


def fix_config(default_settings, old_settings=None):
    old_settings = old_settings or load()
    to_update = {}

    for key, default_value in default_settings.items():
        if key not in old_settings:
            to_update[key] = default_value

    update(to_update, old_settings=old_settings)


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