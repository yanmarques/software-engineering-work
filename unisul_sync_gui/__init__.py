from . import login
from .app import context

import sys


def main():
    context.windows['login'] = login.window.Login()
    return context.app.exec_()
