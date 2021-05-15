from . import plugins, config
from .util import logger
from .app import context
import qasync

import logging
import asyncio


def setup_logging():
    '''
    Configure logging to use file handler
    '''

    log_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    log_path = config.logging_name()
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_fmt)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)


def show():
    qasync.run(_start_gui())


async def _start_gui():
    setup_logging()

    remember_me = context.config.get('rememberme', False)

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
        remember_me = False
    else:
        # start plugin manager normally
        plugin = plugins.PluginManager()
        plugin.register()
    
    logged_from_rememberme = False

    if remember_me:
        logged_from_rememberme = await context.auth_manager.from_rememberme()
        

    context.signals.opening.emit()

    try:
        if logged_from_rememberme:
            logger.info('user already logged in, no need to login')
            context.signals.auth_done.emit()
        else:
            context.signals.auth_failed.emit()       

        context.signals.started.emit(plugin)
    except Exception as err:
        print(err)
        # context.signals.closing.emit()

    loop = asyncio.get_event_loop()
    await loop.create_future()
