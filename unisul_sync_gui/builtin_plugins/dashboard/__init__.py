from . import window
from .. import util
from ... import app


class AuthDoneHandler(util.PluginStarter):
    def init(self):
        self.dashboard = window.Dashboard()

    def opening(self):
        app.context.signals.auth_done.connect(self.open_dashboard)

    def open_dashboard(self):
        print('opening dashboard')
        app.context.windows['dashboard'] = self.dashboard
        self.dashboard.show()
    
    def closing(self):
        self.dashboard.close()


plugin = AuthDoneHandler