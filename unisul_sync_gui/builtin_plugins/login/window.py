from . import screen
from .. import util
from ...app import context
from ...util import logger
from ...crawler import auth
from PyQt5 import QtCore, QtWidgets, QtGui
import qasync 


class LoginDialog(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, parent=None) -> None:
        '''
        Shows a login dialog to authenticate into application.
        '''

        super().__init__(parent)

        # use here to store login qthread
        self.login_runner = None
            
    def show(self) -> None:
        '''
        Display dialog in desktop graphical interface.
        '''

        self.setupUi(self)

        # steal focus for the user field
        self.user_input.setFocus(QtCore.Qt.NoFocusReason)

        # register validators for every input
        list(map(self._field_non_empty_validator, (
            self.user_input,
            self.password_input
        )))

        self.password_input.returnPressed.connect(self.on_login_btn_cliked)
        self.login_button.clicked.connect(self.on_login_btn_cliked)

        self.remember_checkbox.setChecked(context.config.get('rememberme', True))
        self.remember_checkbox.clicked.connect(self.on_rememberme_changed)

        # maybe fill user when exists
        # credentials = app.default_auth_manager().load_creds()
        # if credentials:
        #     self.user_input.setText(credentials[0])
        #     self.password_input.setText(credentials[1])

        super().show()
    
    @qasync.asyncSlot()
    async def on_login_btn_cliked(self) -> None:
        '''
        Event handler for login button. It calls the authentication
        function in the background and return an action to the user
        based on whether authentication has succeeded or not.
        '''

        self.login_button.setEnabled(False)

        is_logged_in = False

        try:
            is_logged_in = await self._perform_login()
        except Exception as err:
            logger.error(str(err), exc_info=err)
        
        self.login_button.setEnabled(True)
        
        if is_logged_in:
            self.on_auth_success()
        else:
            self.on_auth_failed()

    async def _perform_login(self) -> bool:
        '''
        Callback that try to authenticate with user credentials.
        '''

        logger.debug('performing login attempt')

        login = self.user_input.text()
        password = self.password_input.text()

        is_logged_in = await context.auth_manager.from_creds(login, 
                                                     password, 
                                                     rememberme=self._rememberme)

        logger.debug('auth result: %s', is_logged_in)
        return is_logged_in

    def on_rememberme_changed(self, event) -> None:
        '''
        Event handler for remember me checkbox.
        '''

        context.update_config(dict(rememberme=self._rememberme))

    def on_auth_failed(self):
        '''
        Handle when authentication failed.
        '''

        self.password_input.clear()
    
        util.show_dialog('E-mail ou senha inválidos',
                         icon=QtWidgets.QMessageBox.Warning,
                         parent=self)

    def on_auth_success(self):
        '''
        Handle when authentication succeeded.
        '''

        # close myself
        self.close()

        # dispatch event
        context.signals.auth_done.emit()
    
    def _field_non_empty_validator(self, input_widget):
        '''
        Register a validator for the given widget.
        '''

        regex = QtCore.QRegExp(".+")
        non_empty = QtGui.QRegExpValidator(regex, input_widget)
        input_widget.setValidator(non_empty)

    @property
    def _rememberme(self):
        '''
        Helper for checking whether the remember checkbox
        is checked.
        '''

        return self.remember_checkbox.isChecked()
