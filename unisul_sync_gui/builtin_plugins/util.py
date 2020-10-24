from ..app import context
from ..signals import pysignal
from PyQt5.QtWidgets import QFileDialog

import abc


def select_directory(parent=None):
    dialog = QFileDialog(parent=parent)
    dialog.setFileMode(QFileDialog.DirectoryOnly)
    
    if dialog.exec_():
        directories = dialog.selectedFiles()
        if directories:
            return directories[0]


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

