from ..app import context
from ..signals import pysignal
from PyQt5 import QtWidgets, QtCore

import abc


def select_directory(parent=None):
    dialog = QtWidgets.QFileDialog(parent=parent)
    dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
    
    if dialog.exec_():
        directories = dialog.selectedFiles()
        if directories:
            return directories[0]


def clear_layout(layout: QtWidgets.QLayout):
    if isinstance(layout, QtWidgets.QFormLayout):
        count = layout.rowCount()
    else:
        count = layout.count()

    for _ in range(count):
        layout.itemAt(0).widget().setParent(None)


class WidgetBuilder(QtWidgets.QWidget):
    def label(self, text, parent=None):
        label = self._widget(QtWidgets.QLabel, parent)
        label.setText(self._translate(text))
        return label

    def checkbox(self, on_change, initial_value=False, parent=None):
        def on_change_wrapper(state):
            value = True if state == QtCore.Qt.Checked else False
            on_change(value)

        checkbox = self._widget(QtWidgets.QCheckBox, parent)
        checkbox.setChecked(initial_value)
        checkbox.stateChanged.connect(on_change_wrapper)
        return checkbox

    def combobox(self, 
                 on_change, 
                 items, 
                 parent=None, 
                 tooltips=[], 
                 index=0):
        combobox = self._widget(QtWidgets.QComboBox, parent)
        combobox.addItems(['' for _ in range(len(items))])
        
        combobox.activated.connect(on_change)
        
        for text_index, text in enumerate(items):
            combobox.setItemText(text_index, self._translate(text))

        for tooltip_index, tooltip in enumerate(tooltips):
            combobox.setItemData(tooltip_index, 
                                 self._translate(tooltip), 
                                 QtCore.Qt.ToolTipRole)

        if tooltips:
            combobox.setToolTip(self._translate(tooltips[index]))

        combobox.setCurrentIndex(index)

        return combobox

    def button(self, on_click, text, parent=None):
        button = self._widget(QtWidgets.QToolButton, parent)
        button.clicked.connect(on_click)
        button.setText(self._translate(text))
        return button

    def _translate(self, text):
        return QtCore.QCoreApplication.translate(self.objectName(), text)

    def _widget(self, widget_class, parent=None):
        return widget_class(parent=parent or self)


class PluginStarter(abc.ABC):
    def __init__(self):
        super().__init__()
        context.signals.started.connect(self.start)
        self.init()

    def init(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass


class SignalAlreadyExists(Exception):
    pass


class PluginDispatch(abc.ABC):
    def __init__(self):
        super().__init__()
        for signal in self.signals():
            if hasattr(context.signals, signal):
                raise SignalAlreadyExists(f'Signal already exists in the context: {signal}')
            setattr(context.signals, signal, pysignal())
        self.init()

    def init(self):
        pass

    @abc.abstractmethod
    def signals(self):
        pass

