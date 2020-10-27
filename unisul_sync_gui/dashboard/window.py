from . import screen
from .. import config, widgets
from ..builtin_plugins import util
from ..app import context
from PyQt5 import QtWidgets

import multiprocessing
import platform


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

        # use here to store logout qthread
        self.logout_runner = None

        self.show()
        context.signals.landed.emit(sender=self)

    def on_logout(self, event):
        msg = widgets.ConfirmationMessageBox(default_accept=False)
        msg.setText('Tem certeza que deseja sair?')
        if msg.is_accepted():
            login = context.windows['login']

            def on_logout_done():
                self.close()
                login_kwargs = dict(ignore_disk_creds=True)

                if platform.system() == 'Windows':
                    self._fix_windows_logout(login_kwargs)
                else:
                    # reopen a fresh login window, without trying credentials from disk
                    # because we do not want to login again
                    context.windows['login'] = login.new_from_this(**login_kwargs)

            self.setDisabled(True)

            # will actually logout, this invalidates the cookiejar stored in disk
            self.logout_runner = util.GenericCallbackRunner(login.http_auth.logout)
            self.logout_runner.done.connect(on_logout_done)
            self.logout_runner.start()

    def _fix_windows_logout(self, login_kwargs):
        '''
        This avoids the error when logging out then logging in on Windows platforms.

        The actual cause of the error is still unknown.

        Steps to reproduce the error:
        - On Windows, log in then log out
        - Log in again and when the list of subjects and books are loading, it crashes

        Fix:
        Create another process and start the program again from there. The current running
        process is terminated, so the user feels like it just logged him out normally. 
        '''

        from .. import gui

        kwargs = dict(mask_update_checking=True, 
                      login_kwargs=login_kwargs)
        
        # start the program again using a custom configuration
        proc = multiprocessing.Process(target=gui.show, kwargs=kwargs)
        proc.start()

        # exit the running process
        context.exit()