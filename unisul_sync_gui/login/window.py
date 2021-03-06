from . import screen
from unisul_sync_gui import sync, auth
from unisul_sync_gui.app import context
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QRegExpValidator


class Login(QMainWindow, screen.Ui_Dialog):
    def __init__(self, ignore_disk_creds=False, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.http_auth = auth.Authenticator()

        # we may not open the window here
        # when we just logged in from old session
        if self.http_auth.logged:
            self._handle_authenticated_window()
            return

        list(map(self._config_validator, (
            self.user_input,
            self.password_input
        )))

        self.password_input.returnPressed.connect(self.on_login_enter)
        self.login_button.clicked.connect(self.on_login_enter)

        self.remember_checkbox.setChecked(context.config.get('rememberme', True))
        self.remember_checkbox.clicked.connect(self.on_rememberme_changed)

        # we may not show windows here
        # when we could login from credentials in disk
        if not ignore_disk_creds and self._handle_disk_creds():
            return
        self.show()
            
    def on_login_enter(self, event=None):
        login = self.user_input.text()
        password = self.password_input.text()
        
        if self.http_auth.with_creds(login, 
                                    password, 
                                    rememberme=self._rememberme):
            self.on_success()
        else:
            self.on_failed()

    def on_rememberme_changed(self, event):
        context.update_config(dict(rememberme=self._rememberme))

    def on_failed(self):
        self.password_input.setText('')
    
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText('Usuário ou senha inválidos')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def on_success(self):
        print('Haha man')
        self._handle_authenticated_window()
    
    def _config_validator(self, input_widget):
        empty_in_validator = QRegExpValidator(QRegExp(".+"), input_widget)
        input_widget.setValidator(empty_in_validator)

    @property
    def _rememberme(self):
        return self.remember_checkbox.isChecked()

    def _handle_disk_creds(self):
        if self._rememberme and self.http_auth.try_from_disk():
            self._handle_authenticated_window()
            return True

    def new_from_this(self, *args, **kwargs):
        return Login(*args, **kwargs)

    def _handle_authenticated_window(self):
        self.close()
        context.windows['subjects'] = sync.window.Listing()