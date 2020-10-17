from ..app import context, cached_property, AppCtxt
from ..sync.window import Listing
from PyQt5.QtWidgets import QMessageBox
import rarfile

import abc
import os
import zipfile
import traceback


class ExtractListener(abc.ABC):
    def __init__(self):
        self.init()
        context.signals.item_completed.connect(self.on_item)

    @abc.abstractproperty
    def strategies(self):
        pass

    # overwritable
    def init(self):
        pass

    def on_item(self, results=None, item=None, info=None):
        books = [book for ok, book in results if ok]
        for book in books:
            path = os.path.join(context.config['sync_dir'], book['path'])
            self.try_extractions(path)

    def try_extractions(self, path):
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
        try:
            rarfile.tool_setup()
            return True
        except rarfile.RarCannotExec:
            return False

    def book_to_extract(self, path):
        return rarfile.is_rarfile(path)

    def extract(self, path):
        with rarfile.RarFile(path) as rar:
            rar.extractall(path=os.path.dirname(path))


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
            RARExtraction(),
            ZIPExtraction(),
        ]

    def init(self):
        context.signals.shown.connect(self._check_rar_support)

    def _check_rar_support(self, sender):
        if isinstance(sender, Listing) and not RARExtraction().is_supported:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            text = """
Arquivos em formato Rar não suportados para extração.

Para extrair arquivos em formato Rar baixe o programa apropriado.
"""
            msg.setText(text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


plugin = UnpackPlugin