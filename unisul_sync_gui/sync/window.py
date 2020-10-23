from . import screen
from unisul_sync_gui import config
from unisul_sync_gui.app import context
from PyQt5.QtWidgets import (
    QMainWindow,   
    QMessageBox,
)

class Listing(QMainWindow, screen.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # signaling
        self.logout_button.triggered.connect(self.on_logout)

        context.signals.showing.emit(sender=self)
        self.show()
        context.signals.shown.emit(sender=self)

    def on_logout(self, event):
        msg = QMessageBox(parent=self)
        msg.setIcon(QMessageBox.Question)
        msg.setText('Tem certeza que deseja sair?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            login = context.windows['login'] 
            
            # actully logout, this invalidates the cookiejar stored in disk
            login.http_auth.logout()

            self.close()

            # reopen a fresh login window, without trying credentials from disk
            # because we do not want to login again
            context.windows['login'] = login.new_from_this(ignore_disk_creds=True)