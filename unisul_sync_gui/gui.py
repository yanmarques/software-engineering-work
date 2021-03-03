from . import plugins, login
from .app import context


def show():
    login_kwargs = dict()

    if context.config.get('fixing_windows_logout_error', False):
        # ensure we do not come here again
        # unless explicitly conducted to
        context.update_config({'fixing_windows_logout_error': False})

        # save original value from config
        original_update_chk = context.config['check_updates_on_open']

        # set that we do not want to check for updates
        # this come from updates plugin
        context.update_config({'check_updates_on_open': False})

        # start the plugin manager without checking for updates
        plugin = plugins.PluginManager()
        plugin.register()

        # restore original update checking value
        context.update_config({'check_updates_on_open': original_update_chk})

        # say to authenticator to ignore disk credentials
        # because we are trying to show the login page
        login_kwargs.update(ignore_disk_creds=True)
    else:
        # start plugin manager normally
        plugin = plugins.PluginManager()
        plugin.register()

    context.signals.opening.emit()

    try:
        context.windows['login'] = login.window.Login(**login_kwargs)
        
        context.signals.started.emit(plugin)

        return context.app.exec_()
    finally:
        context.signals.closing.emit()
