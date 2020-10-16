from ..app import context, cached_property, AppCtxt
from ..login.window import Login
from ..book_bot.spiders.sync_spider import BookDownloaderSpider
from patoolib import extract_archive, test_archive, ArchivePrograms
from patoolib.util import PatoolError

from distutils.spawn import find_executable
import abc
import os
import sys
import zipfile
import importlib
import subprocess


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


class UnarExtraction(ExtractionStrategy):
    @property
    def is_supported(self):
        return self._extract_command is not None

    @cached_property
    def _extract_command(self):
        return find_executable('unar')

    @cached_property
    def _list_command(self):
        return find_executable('lsar')

    def book_to_extract(self, path):
        cmd = [self._list_command, path]
        return subprocess.call(cmd) == 0

    def extract(self, path):
        directory = os.path.dirname(path)
        cmd = [self._extract_command, '-o', directory, path]
        ret_code = subprocess.call(cmd)
        if ret_code != 0:
            print('Something went wrong extracting using unar')


class PatoolExtraction(ExtractionStrategy):
    def book_to_extract(self, path):
        try:
            test_archive(path)
            return True
        except PatoolError:
            return False

    def extract(self, path):
        try:
            extract_archive(path, 
                            outdir=os.path.dirname(path),
                            interactive=False)
            print('extracted')
        except PatoolError as exc:
            print('error')
            print(exc)


class UnpackPlugin(ExtractListener):
    @cached_property
    def strategies(self):
        return [
            UnarExtraction(),
            PatoolExtraction()
        ]


plugin = UnpackPlugin