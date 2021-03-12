from . import screen
from .. import util
from ...crawler import auth
from ...app import context
from PyQt5 import QtCore, QtWidgets, QtGui


class Login(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # use here to store login qthread
        self.login_runner = None
            
    def show(self):
        self.setupUi(self)

        self.user_input.setFocus(QtCore.Qt.NoFocusReason)

        list(map(self._config_validator, (
            self.user_input,
            self.password_input
        )))

        self.password_input.returnPressed.connect(self.on_login_enter)
        self.login_button.clicked.connect(self.on_login_enter)

        self.remember_checkbox.setChecked(context.config.get('rememberme', True))
        self.remember_checkbox.clicked.connect(self.on_rememberme_changed)

        # maybe fill user when exists
        credentials = self.auth_manager.load_creds()
        if credentials:
            self.user_input.setText(credentials[0])
            self.password_input.setText(credentials[1])

        super().show()
            
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
        #self.login_runner = util.GenericCallbackRunner(self.auth_manager.from_creds)
        #self.login_runner._args = (login, password)
        #self.login_runner._kwargs = dict(rememberme=self._rememberme)
        #self.login_runner.done.connect(on_login_done)
        #self.login_runner.start()

    def on_rememberme_changed(self, event):
        context.update_config(dict(rememberme=self._rememberme))

    def on_failed(self):
        self.password_input.clear()
    
        util.show_dialog('E-mail ou senha inválidos',
                         icon=QtWidgets.QMessageBox.Warning,
                         parent=self)

    def on_success(self):
        self.close()
        context.signals.auth_done.emit()
    
    def _config_validator(self, input_widget):
        regex = QtCore.QRegExp(".+")
        non_empty = QtGui.QRegExpValidator(regex, input_widget)
        input_widget.setValidator(non_empty)

    @property
    def _rememberme(self):
        return self.remember_checkbox.isChecked()

    def new_from_this(self, *args, **kwargs):
        return Login(*args, **kwargs)
