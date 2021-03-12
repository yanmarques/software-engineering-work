from . import (
    extractfile, 
    sync_gui, 
    settings, 
    updates,
    help,
    login,
    dashboard,
)


def available_modules():
    return [
        login,
        dashboard,
        help,
        extractfile,
        sync_gui,
        settings,
        updates,
    ]