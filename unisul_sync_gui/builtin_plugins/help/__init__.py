from . import screen
from .. import util
from ... import __version__ as app_version, __author__ as app_author
from ...dashboard.window import Dashboard
from ...app import context
from PyQt5 import QtWidgets, QtCore, QtGui


class AboutDialog(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('Sobre'))
        self.name.setText(self.tr('UnisulSync'))
        self.version.setText(self.tr(app_version))
        self.author.setText(self.tr(app_author))
        self.exec_()


class HelpMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("helpMenu")
        self.setTitle(self.tr('Ajuda'))

        context.signals.help_menu.emit(menu=self)        # pylint: disable=E1101

        self.about_action = QtWidgets.QAction()
        self.about_action.setText(self.tr('Sobre'))
        self.about_action.setIcon(QtGui.QIcon.fromTheme('help-about'))
        self.about_action.triggered.connect(self._open_about)
        self.addAction(self.about_action)

    def _open_about(self):
        AboutDialog()


class HelpGuiPlugin(util.PluginDispatch):
    def init(self):
        context.signals.landing.connect(self.on_landing)

    def signals(self):
        return [
            'help_menu'
        ]

    def on_landing(self, sender: Dashboard = None):
        assert sender
        help_menu = HelpMenu(sender.menubar)
        sender.menubar.addAction(help_menu.menuAction())


plugin = HelpGuiPlugin
