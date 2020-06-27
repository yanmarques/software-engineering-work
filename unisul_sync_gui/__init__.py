from . import login
from .app import context

import sys


def main():
    context.windows['login'] = login.window.Login()
    exit_code = context.app.exec_()
    sys.exit(exit_code)