from . import screen
from ..util import PluginDispatch, PluginStarter
from ...app import context
from PyQt5 import QtWidgets, QtCore

from typing import Tuple
import abc


class PluginTab(PluginStarter):
    def start(self):
        context.signals.settings_tab.connect(self.on_settings_tab)

    def on_settings_tab(self, tab_widget=None):
        assert tab_widget, 'Missing tab widget on event'
        self.add_tab(tab_widget, *self.setting_tab())

    @abc.abstractmethod
    def setting_tab(self) -> Tuple[str, QtWidgets.QWidget]:
        pass

    def add_tab(self, tab_widget, text, tab, _context='MainWindow'):
        tab_widget.addTab(tab, '')
        translation = QtCore.QCoreApplication.translate(_context, text)
        tab_widget.setTabText(tab_widget.indexOf(tab), translation)


class Settings(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self, GeneralTab())

        context.signals.settings_tab.emit(tab_widget=self.tabWidget)
        self.exec_()


class GeneralTab(screen.GenericTab):
    def config(self):
        return [
            self._rememberme(),
            self._default_dashboard_tab(),
        ]

    def _rememberme(self):
        def on_change(self, state):
            context.update_config({'rememberme': state})

        return (self.label('lembrar do login'),
                self.checkbox(on_change, context.config['rememberme']))

    def _default_dashboard_tab(self):
        tab_widget = context.windows['dashboard'].tabWidget

        tabs = [tab_widget.tabText(index)
                for index in range(tab_widget.count())]

        def on_change(index):
            context.update_config({'default_tab': index})

        return (self.label('guia padrão na dashboard'), 
                self.combobox(on_change, tabs))


class SettingsGuiPlugin(PluginDispatch):
    def init(self):
        context.signals.landing.connect(self.on_landing)

    def signals(self):
        return [
            'settings_tab'
        ]

    def on_landing(self, sender=None):
        assert sender is not None
        settings_button = self._get_button(sender)
        sender.opts_menu.addAction(settings_button)

    def _get_button(self, parent):
        button = QtWidgets.QAction(parent=parent)
        button.setObjectName('settings_button')
        button.setText(QtCore.QCoreApplication.translate('MainWindow', 'Configurações'))
        button.triggered.connect(self.on_open)
        return button

    def on_open(self):
        Settings()

    
plugin = SettingsGuiPlugin
