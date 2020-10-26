from . import (
    extractfile, 
    sync_gui, 
    settings, 
    updates,
    help,
)


def available_modules():
    return [
        help,
        extractfile,
        sync_gui,
        settings,
        updates,
    ]