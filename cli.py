from unisul_sync_gui import gui

import sys
import asyncio


def entrypoint():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(gui.show())

    
if __name__ == '__main__':
    sys.exit(entrypoint())