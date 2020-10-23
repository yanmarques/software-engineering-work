from ..app import context
from ..signals import pysignal

import abc


class PluginStarter(abc.ABC):
    def __init__(self):
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

