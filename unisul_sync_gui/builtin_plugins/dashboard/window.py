from . import screen
from .. import util
from ... import widgets, app
from ...crawler import auth
from PyQt5 import QtWidgets

import platform


class Dashboard(QtWidgets.QMainWindow, screen.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # use here to store logout qthread
        self.logout_runner = None

    def show(self):
        self.setupUi(self)

        # signaling
        self.logout_button.triggered.connect(self.on_logout)
        self.close_button.triggered.connect(self.close)

        app.context.signals.landing.emit(sender=self)
        
        self.opts_menu.addAction(self.logout_button)
        self.opts_menu.addAction(self.close_button)
        self.tabWidget.setCurrentIndex(app.context.config.get('default_tab', 0))

        super().show()
        app.context.signals.landed.emit(sender=self)

    def on_logout(self, event):
        msg = widgets.ConfirmationMessageBox(default_accept=False)
        msg.setText('Tem certeza que deseja sair?')
        if msg.is_accepted():
            # ensure when user logs out, and eventually logs in
            # again, the app will not face as a first time user
            self._maybe_reset_first_time()

            def on_logout_done():
                self.close()

                if platform.system() == 'Windows':
                    self._fix_windows_logout()
                else:
                    # reopen a fresh login window, without trying credentials from disk
                    # because we do not want to login again
                    app.context.signals.auth_failed.emit()

            self.setDisabled(True)

            # will actually logout, this invalidates the cookiejar stored in disk
            #self.logout_runner = util.GenericCallbackRunner(self.auth_manager.logout)
            #self.logout_runner.done.connect(on_logout_done)
            #self.logout_runner.start()
        
    def _maybe_reset_first_time(self):
        if app.context.config['first_time']:
            app.context.update_config({'first_time': False})

    def _fix_windows_logout(self):
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
        from ..updates import autoupdate

        import multiprocessing

        # sinalize to the incoming process that we are avoiding
        # the windows logout error, so it can act accordingly
        app.context.update_config({'fixing_windows_logout_error': True})

        # are we a bundled app
        if autoupdate.can_make_it():
            # re-start the app
            autoupdate.relaunch_app()
        else:
            # as this condition are only generally met by developers
            # we do not have to worry much about it, but it is bad anyway
            #
            # this will create a different process everytime the user logs out
            # each process being a child of the latter
            multiprocessing.Process(target=gui.show).start()

        # exit the running process
        app.context.exit()