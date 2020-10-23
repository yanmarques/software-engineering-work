from .util import PluginStarter
from ..app import context, cached_property, AppCtxt
from ..config import just_once
from PyQt5.QtWidgets import QMessageBox
import rarfile

import abc
import os
import zipfile
import traceback
import platform


class ExtractListener(PluginStarter):
    def start(self):
        context.signals.item_completed.connect(self._on_item)
        context.signals.syncing.connect(self._set_loader)

    @abc.abstractproperty
    def strategies(self):
        pass

    def init(self):
        self._loader, self._count = None, 0
        self._index, self._per_bump = 0, 0

    def _set_loader(self, **kwargs):
        self._loader = kwargs.get('loader')
        self._count = kwargs.get('count')
        self._index = 0
        self._per_bump = 100 / self._count

    def _on_item(self, results=None, item=None, info=None):
        books = [book for ok, book in results if ok]
        for book in books:
            path = os.path.join(context.config['sync_dir'], book['path'])
            self._try_extractions(path)

    def _try_extractions(self, path):
        for strategy in self.strategies:
            if not strategy.is_supported:
                continue

            try:
                if strategy.maybe_extract(path):
                    break
            except AttributeError:
                raise
            except Exception:
                traceback.print_exc()
            finally:
                pass
                # os.unlink(path)

        self._loader.bump.emit(self._per_bump)


class ExtractionStrategy(abc.ABC):
    @property
    def is_supported(self):
        return True

    @abc.abstractmethod
    def book_to_extract(self, path):
        pass

    @abc.abstractmethod
    def extract(self, path):
        pass

    def maybe_extract(self, path):
        if self.book_to_extract(path):
            self.extract(path)
            return True
        return False


class RARExtraction(ExtractionStrategy):
    @property
    def is_supported(self):
        if rarfile.__version__ == '4.0':
            try:
                rarfile.tool_setup()
            except rarfile.RarCannotExec:
                return False
            return True

        #
        # handle old rarfile versions
        #
        available_tools = {
            rarfile.UNRAR_TOOL: [],
            rarfile.ALT_TOOL: rarfile.ALT_CHECK_ARGS,   # pylint: disable=E1101
        }

        for tool, check_args in available_tools.items():
            try:
                cmd = [tool] + list(check_args)
                rarfile.custom_check(cmd, True) # pylint: disable=E1101
                return True
            except rarfile.RarCannotExec:
                pass
        return False

    def book_to_extract(self, path):
        return rarfile.is_rarfile(path)

    def extract(self, path):
        with rarfile.RarFile(path) as rar:
            rar.extractall(path=os.path.dirname(path))


class WinRARExtraction(RARExtraction):
    def init(self):
        self._winrar_path = None
        self.is_supported

    @cached_property
    def is_supported(self):
        if platform.system() != 'Windows':
            return False

        winrar_dir = 'WinRAR'

        paths = [
            os.getenv('ProgramFiles'),
            os.getenv('ProgramFiles(x86)'),
        ]

        for path in paths:
            winrar_path = os.path.join(path, winrar_dir)
            if os.path.exists(winrar_path):
                self._winrar_path = winrar_path
                return True

        return False
            
    def book_to_extract(self, path):
        self._wrap_unrar_tool()
        return super().book_to_extract(path)

    def extract(self, path):
        self._wrap_unrar_tool()
        return super().extract(path)

    def _wrap_unrar_tool(self):
        rarfile.UNRAR_TOOL = os.path.join(self._winrar_path, 'UnRAR.exe')
        rarfile.CURRENT_SETUP = None


class ZIPExtraction(ExtractionStrategy):
    def book_to_extract(self, path):
        return zipfile.is_zipfile(path)

    def extract(self, path):
        with zipfile.ZipFile(path) as zip:
            zip.extractall(path=os.path.dirname(path))


class UnpackPlugin(ExtractListener):
    @cached_property
    def strategies(self):
        return [
            ZIPExtraction(),
        ] + self.rar_extractors

    @cached_property
    def rar_extractors(self):
        return [
            RARExtraction(),
            WinRARExtraction()
        ]

    def init(self):
        super().init()
        context.signals.landed.connect(self.on_landed)

    def on_landed(self, sender=None):
        assert sender is not None
        self._check_rar_support(self, sender)

    @just_once
    def _check_rar_support(self, dashboard):
        if not any(obj.is_supported for obj in self.rar_extractors):
            msg = QMessageBox(parent=dashboard)
            msg.setWindowTitle('Plugin - Extração de Arquivos')
            msg.setIcon(QMessageBox.Warning)
            text = """
Arquivos em formato Rar não suportados para extração.

Para extrair arquivos em formato Rar baixe o programa apropriado.
"""
            msg.setText(text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


plugin = UnpackPlugin