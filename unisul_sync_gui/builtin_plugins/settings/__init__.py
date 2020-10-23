from . import screen
from ..util import PluginDispatch
from ...app import context
from PyQt5 import QtWidgets, QtCore


class Settings(screen.Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)



class SettingsGuiPlugin(PluginDispatch):
    def init(self):
        context.signals.landing.connect(self.on_landing)

    def signals(self):
        return [
            
        ]

    def on_landing(self, sender=None):
        assert sender is not None
        settings_button = QtWidgets.QAction(sender)
        settings_button.setObjectName('settings_button')
        sender.opts_menu.addAction(settings_button)
        settings_button.setText(QtCore.QCoreApplication.translate('MainWindow', 'Configurações'))

    
plugin = SettingsGuiPlugin
