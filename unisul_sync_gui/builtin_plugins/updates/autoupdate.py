from . import texts, checker, screen
from .. import util
from ...app import context
from PyQt5 import QtWidgets, QtCore

import zipfile
import os
import sys
import tempfile
import shutil


def can_make_it():
    '''
    Return whether the app is bundled.

    see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    '''

    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def relaunch_app():
    '''
    Launch an independent version of the app. 
    '''

    os.startfile(sys.executable)        # pylint: disable=E1101


def make(update_checker: checker.UpdateChecker):
    assert can_make_it(), 'Application is not bundled by pyinstaller, could not continue'
    tmpfile = tempfile.mkstemp()[1]
    downloader = update_checker.build_downloader(tmpfile)
    update_applier = WindowsUpdateApplier(downloader)
    update_applier.update_app()


def filesize(size_in_bytes):
    sizes = (
        'KB',
        'MB',
        'GB',
        'TB'        
    )

    def format_size(suffix):
        return '{:10.2f} {}'.format(size_in_bytes, suffix).strip()

    # is it just bytes?
    if size_in_bytes < 1024:
        return format_size('B')
    
    for candidate in sizes:
        size_in_bytes = size_in_bytes / 1024
        if size_in_bytes < 1024:
            return format_size(candidate)

    # if we got here just return the latest candidate
    return format_size(candidate)


class AssetDownloadLoading(QtWidgets.QDialog):
    def __init__(self, 
                 downloader: checker.AssetDownloader, 
                 parent=None):
        super().__init__(parent=parent)
        self.setupUi()
        self.downloader = downloader
        self.downloader.got_response.connect(self._received_response)
        self.downloader.chunk_wrote.connect(self._bump_progress)

        self.download_len, self.total_rcv = 0, 0
        self.per_chunk, self.progress = 0, 0
        self.download_len_label = None

    def setupUi(self):
        self.resize(300, 90)
        self.mainGridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout = QtWidgets.QGridLayout()
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label)
        self.prog_bar = QtWidgets.QProgressBar()
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(0)
        self.gridLayout.addWidget(self.prog_bar)
        self.mainGridLayout.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self.tr('Baixando atualização'))
        self.label.setText(self.tr('Enviando requisição...'))

    def _received_response(self, download_len):
        self.download_len = filesize(download_len)
        self.per_chunk = (self.downloader.chunk_size * 100) / download_len
        self._update_recv(0)

    def _bump_progress(self, chunk_rcv):
        self.progress += self.per_chunk
        self.prog_bar.setValue(self.progress)
        self._update_recv(chunk_rcv)

    def _update_recv(self, rcv_length):
        self.total_rcv += rcv_length
        total_size_rcv = filesize(self.total_rcv)
        self.label.setText(self.tr(f'{total_size_rcv} de {self.download_len}'))


class WindowsUpdateApplier(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, downloader: checker.AssetDownloader, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.label.setText(self.tr('Atualizando'))

        # get pyinstaller specific parameter
        # see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
        self.installation_path = sys._MEIPASS       # pylint: disable=E1101

        self.downloader = downloader
        self.downloader.done.connect(self._on_download_done)
        self.download_loading = AssetDownloadLoading(self.downloader)

        self.update_loading = util.LoadingPoints(self.loading_label)
        self.update_loading.done.connect(self.close)

        self.update_runner = util.GenericCallbackRunner(self._apply_update)
        self.update_runner.done.connect(self._on_update_done)

    def update_app(self):
        self.downloader.start()
        self.download_loading.exec_()
        
    def _apply_update(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            # extract everything under a temporary directory
            with zipfile.ZipFile(self.downloader.filepath) as zip:
                zip.extractall(tmpdir)

            # get the first item in the directory, it should be our 
            # application
            main_directory = os.listdir(tmpdir)[0]

            # move extracted contents into the installation directory
            target_path = os.path.join(tmpdir, main_directory)
            shutil.copytree(target_path,        # pylint: disable=E1123
                            self.installation_path,
                            dirs_exist_ok=True)

    def _on_download_done(self):
        self.download_loading.close()
        self.update_loading.start()
        self.update_runner.start()
        self.exec_()

    def _on_update_done(self):
        self.update_loading.do_stop.emit()
        util.show_dialog(texts.windows_autoupdate_finished)

        # launches the updated app
        relaunch_app()

        # exit from current application
        context.exit(0)