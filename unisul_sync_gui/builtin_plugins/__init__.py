from . import (
    extractfile, 
    sync_gui, 
    settings, 
    updates,
)


def available_modules():
    return [
        extractfile,
        sync_gui,
        settings,
        updates,
    ]