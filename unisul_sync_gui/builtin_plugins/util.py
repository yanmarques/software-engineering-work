from ..util import logger
from ..app import context
from ..signals import pysignal
from PyQt5 import QtWidgets, QtCore

import abc
import asyncio


def select_directory(parent=None):
    return _select_files(QtWidgets.QFileDialog.DirectoryOnly, parent=parent)


def select_file(parent=None, filename=None):
    return _select_files(QtWidgets.QFileDialog.FileMode, 
                         parent=parent,
                         filename=filename)


def _select_files(mode, 
                  parent=None, 
                  first=True, 
                  filename=None):
    dialog = QtWidgets.QFileDialog(parent=parent)
    dialog.setFileMode(mode)
    if filename:
        dialog.selectFile(filename)

    if dialog.exec_():
        files = dialog.selectedFiles()
        if not first:
            return files

        if files:
            return files[0]


def show_dialog(body, icon=None, title=None, parent=None):
    msg = QtWidgets.QMessageBox(parent=parent)
    if icon:
        msg.setIcon(icon)
    if title:
        msg.setWindowTitle(msg.tr(title))
    msg.setText(msg.tr(body))
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()


def clear_layout(layout: QtWidgets.QLayout):
    if isinstance(layout, QtWidgets.QFormLayout):
        count = layout.rowCount()
    else:
        count = layout.count()

    for _ in range(count):
        layout.itemAt(0).widget().setParent(None)


class LoadingPoints(QtCore.QThread):
    do_stop = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()

    def __init__(self, label, points_len=5):
        super().__init__()
        self.points_len = points_len
        self._loading_label = label
        self.stopped = False
        self.do_stop.connect(self._stop_from_out)

    def run(self):
        while not self.stopped:
            self.usleep(250000)
            text = self._loading_label.text()

            if len(text) < self.points_len:
                self._loading_label.setText(self.tr(f'{text}.'))
            else:
                self._loading_label.setText('')
        self.done.emit()

    def _stop_from_out(self):
        self.stopped = True



class GenericCallbackRunner(QtCore.QThread):
    done = QtCore.pyqtSignal(object)
    err = QtCore.pyqtSignal(Exception)

    def __init__(self, callback, *args, **kwargs):
        super().__init__()
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self.err.connect(self.default_error_handler)

    def default_error_handler(self, error):
        logger.error(str(error), exc_info=error)

    def run(self):
        try:
            result = self._callback(*self._args, **self._kwargs)
            self.done.emit(result)
        except Exception as exc:
            self.err.emit(exc)


class CoroRunner(GenericCallbackRunner):
    def __init__(self, coro, *args, **kwargs) -> None:
        '''
        Generic class which runs a coroutine with in a 
        QThread.

        The class handles calling the coroutine from a
        synchronous context.
        '''
        super().__init__(self._sync_run, *args, **kwargs)

        self._coro = coro

        # important, create a new loop everytime
        self._loop = asyncio.new_event_loop()

    def _sync_run(self, *_, **__):
        return self._loop.run_until_complete(self._async_run())

    async def _async_run(self):
        return await self._coro(*self._args, **self._kwargs)


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
        context.signals.opening.connect(self.opening)
        context.signals.opening.connect(self.closing)
        self.init()

    def init(self):
        pass

    def start(self):
        pass

    def opening(self):
        pass

    def closing(self):
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

