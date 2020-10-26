from . import screen
from .. import auth
from ..app import context
from ..builtin_plugins import util
from ..dashboard.window import Dashboard
from PyQt5 import QtCore, QtWidgets, QtGui


class Login(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, ignore_disk_creds=False, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.user_input.setFocus(QtCore.Qt.NoFocusReason)

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

        # maybe fill user when exists
        credentials = auth.load_keys()
        if credentials:
            self.user_input.setText(credentials[0])
            self.password_input.setText(credentials[1])

        # use here to store login qthread
        self.login_runner = None
            
        self.show()
            
    def on_login_enter(self, event=None):
        login = self.user_input.text()
        password = self.password_input.text()

        def on_login_done(logged_in):
            if logged_in:
                self.on_success()
            else:
                self.setDisabled(False)
                self.on_failed()

        self.setDisabled(True)
        self.login_runner = util.GenericCallbackRunner(self.http_auth.with_creds)
        self.login_runner._args = (login, password)
        self.login_runner._kwargs = dict(rememberme=self._rememberme)
        self.login_runner.done.connect(on_login_done)
        self.login_runner.start()

    def on_rememberme_changed(self, event):
        context.update_config(dict(rememberme=self._rememberme))

    def on_failed(self):
        self.password_input.clear()
    
        util.show_dialog('E-mail ou senha inválidos',
                         icon=QtWidgets.QMessageBox.Warning,
                         parent=self)

    def on_success(self):
        self._handle_authenticated_window()
    
    def _config_validator(self, input_widget):
        regex = QtCore.QRegExp(".+")
        non_empty = QtGui.QRegExpValidator(regex, input_widget)
        input_widget.setValidator(non_empty)

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
        context.windows['dashboard'] = Dashboard()