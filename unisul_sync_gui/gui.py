from . import plugins
from .app import context, create_auth_manager


async def show():
    auto = True

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
        auto = False
    else:
        # start plugin manager normally
        plugin = plugins.PluginManager()
        plugin.register()

    auth_manager = await create_auth_manager(auto=auto, 
                                       remember_me=context.config.get('rememberme'))

    context.signals.opening.emit()

    try:
        if auth_manager.is_logged_in:
            context.signals.auth_done.emit()
        else:
            context.signals.auth_failed.emit()

        # close authentication manager        
        await auth_manager.close()

        context.signals.started.emit(plugin)

        return context.app.exec_()
    finally:
        context.signals.closing.emit()
