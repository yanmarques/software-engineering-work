from unisul_sync_gui import gui

import sys


def entrypoint():
    # start app
    return gui.show()

    
if __name__ == '__main__':
    sys.exit(entrypoint())