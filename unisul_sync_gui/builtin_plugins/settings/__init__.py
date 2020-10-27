from . import screen
from ..util import PluginDispatch, PluginStarter, WidgetBuilder
from ...app import context
from PyQt5 import QtWidgets, QtCore, QtGui

from typing import Tuple
import abc


class PluginTab(PluginStarter):
    def start(self):
        context.signals.settings_tab.connect(self.on_settings_tab)      # pylint: disable=E1101

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


class SettingProvider(WidgetBuilder):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self._layout, self._row_index = None, 0
        self.init()

    def init(self):
        pass

    def build_form_layout(self, index, form_layout: QtWidgets.QFormLayout):
        self._layout = form_layout
        self._row_index = index
        self._build()

    def rebuild(self):
        self._layout.removeRow(self._row_index)
        self._build()

    def _build(self):
        label, field = self.fields()
        self.insert_widgets(label=label, field=field)

    def insert_widgets(self, label=None, field=None):
        if label:
            self._layout.setWidget(self._row_index, 
                                   QtWidgets.QFormLayout.LabelRole, 
                                   label)
        
        if field:
            self._layout.setWidget(self._row_index, 
                                   QtWidgets.QFormLayout.FieldRole, 
                                   field)

    def fields(self):
        self._raise_not_implemented('field')

    @property
    def provides(self):
        self._raise_not_implemented('provides')

    @property
    def current_value(self):
        return context.config[self.provides]

    def update(self, value):
        context.signals.settings_changing.emit(provider=self,   # pylint: disable=E1101
                                            new_value=value)
        context.update_config({self.provides: value})

    def _raise_not_implemented(self, method):
        class_name = self.__class__.__name__
        raise NotImplementedError(f'Missing [{method}] method implementation at {class_name}.')

    def _widget(self, widget_class, parent=None):
        return widget_class(parent=parent or self.parent())


class Settings(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self, GeneralTab())

        context.signals.settings_tab.emit(tab_widget=self.tabWidget)    # pylint: disable=E1101
        self.gridLayout.addWidget(self.tabWidget)
        self.exec_()


class GeneralTab(screen.GenericTab):
    def config(self):
        return [
            RememberMeSetting,
            DefaultDashboardTabSetting,
        ]


class RememberMeSetting(SettingProvider):
    def fields(self):
        return (self.label('lembrar do login'),
                self.checkbox(self.update, self.current_value))

    @property
    def provides(self):
        return 'rememberme'


class DefaultDashboardTabSetting(SettingProvider):
    def fields(self):
        tab_widget = context.windows['dashboard'].tabWidget

        tabs = [tab_widget.tabText(index)
                for index in range(tab_widget.count())]

        return (self.label('guia padrão na dashboard'), 
                self.combobox(self.update, tabs, index=self.current_value))

    @property
    def provides(self):
        return 'default_tab'


class SettingsGuiPlugin(PluginDispatch):
    def init(self):
        context.signals.landing.connect(self.on_landing)

    def signals(self):
        return [
            'settings_tab',
            'settings_changing',
        ]

    def on_landing(self, sender=None):
        assert sender is not None
        settings_button = self._get_button(sender)
        sender.opts_menu.addAction(settings_button)

    def _get_button(self, parent):
        button = QtWidgets.QAction(parent=parent)
        button.setObjectName('settings_button')
        button.setIcon(QtGui.QIcon.fromTheme('preferences-system'))
        button.setText(button.tr('Configurações'))
        button.triggered.connect(self.on_open)
        return button

    def on_open(self):
        Settings()

    
plugin = SettingsGuiPlugin
