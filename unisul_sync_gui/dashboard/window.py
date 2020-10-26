from . import screen
from .. import config, widgets
from ..app import context
from PyQt5 import QtWidgets


class Dashboard(QtWidgets.QMainWindow, screen.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # signaling
        self.logout_button.triggered.connect(self.on_logout)
        self.close_button.triggered.connect(self.close)

        context.signals.landing.emit(sender=self)
        
        self.opts_menu.addAction(self.logout_button)
        self.opts_menu.addAction(self.close_button)
        self.tabWidget.setCurrentIndex(context.config.get('default_tab', 0))

        self.show()
        context.signals.landed.emit(sender=self)

    def on_logout(self, event):
        msg = widgets.ConfirmationMessageBox(default_accept=False)
        msg.setText('Tem certeza que deseja sair?')
        if msg.is_accepted():
            login = context.windows['login'] 
            
            # actully logout, this invalidates the cookiejar stored in disk
            login.http_auth.logout()

            self.close()

            # reopen a fresh login window, without trying credentials from disk
            # because we do not want to login again
            context.windows['login'] = login.new_from_this(ignore_disk_creds=True)