from . import plugins, login
from .app import context

import sys


def on_close():
    print('SAINDO')
    context.update_config({'first_time': False})


def _register_events(include=None):
    # context.signals.opening.connect()
    context.signals.closing.connect(on_close)


def main():
    _register_events()

    plugin = plugins.PluginManager()

    context.signals.opening.emit()

    try:
        context.windows['login'] = login.window.Login()
        
        context.signals.started.emit(plugin)

        return context.app.exec_()
    finally:
        context.signals.closing.emit()

    return 1
