from . import plugins, login
from .app import context

import sys


def on_close():
    print('SAINDO')
    context.update_config({'first_time': False})


def _register_events(include=None):
    # context.signals.opening.connect()
    context.signals.closing.connect(on_close)


def show(mask_update_checking=False, 
         login_kwargs=dict()):
    _register_events()

    # disable update checking when needed
    if mask_update_checking:
        original_update_chk = context.config['check_updates_on_open']
        context.update_config({'check_updates_on_open': False})

    plugin = plugins.PluginManager()

    # restore original update checking value
    if mask_update_checking:
        context.update_config({'check_updates_on_open': original_update_chk})

    if mask_update_checking:
        context.update_config({'check_updates_on_open': original_update_chk})

    context.signals.opening.emit()

    try:
        context.windows['login'] = login.window.Login()
        
        context.signals.started.emit(plugin)

        return context.app.exec_()
    finally:
        context.signals.closing.emit()

    return 1
