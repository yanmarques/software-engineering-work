from ..app import context, cached_property, AppCtxt
import rarfile

import abc
import os
import zipfile


class ExtractListener(abc.ABC):
    def __init__(self):
        context.signals.item_completed.connect(self.on_item)

    @abc.abstractproperty
    def strategies(self):
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
            except Exception as exc:
                print(exc)
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


plugin = UnpackPlugin