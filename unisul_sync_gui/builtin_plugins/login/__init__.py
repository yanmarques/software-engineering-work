from . import window
from .. import util
from ... import app


class AuthFailedHandler(util.PluginStarter):
    def init(self):
        self.login = window.Login()

    def opening(self):
        app.context.signals.auth_failed.connect(self.open_login)

    def open_login(self):
        self.login.show()

    def closing(self):
        self.login.close()


plugin = AuthFailedHandler