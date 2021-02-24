from . import texts, checker, screen
from .. import util
from ... import dist_util 
from ...app import context
from PyQt5 import QtWidgets, QtCore

import zipfile
import os
import sys
import tempfile
import shutil

UPDATER_KEY = '_installation_path_to_update'


def can_make_it():
    return dist_util.is_bundled()


def relaunch_app():
    '''
    Launch an independent version of the app. 
    '''

    os.startfile(sys.executable)        # pylint: disable=E1101


def current_path():
    return dist_util.cwd()


def get_executable(path=None):
    path = path or current_path()

    # we will assume the same executable of the current one
    executable = os.path.basename(sys.executable)

    return os.path.join(path, executable)


def make(update_checker: checker.UpdateChecker):
    assert can_make_it(), 'Application is not bundled by pyinstaller, could not continue'
    tmpfile = tempfile.mkstemp()[1]
    downloader = update_checker.build_downloader(tmpfile)
    update_down = WindowUpdateDownloader(downloader)
    update_down.download_and_extract()


def maybe_install_update():
    installation_path = context.config.get(UPDATER_KEY)
    if installation_path:
        try:
            win_updater = WindowsUpdateApplier(installation_path)
            win_updater.update()
        finally:
            # assign that there is no need for updates anymore
            context.update_config({UPDATER_KEY: None})


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


class WindowUpdateDownloader(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, downloader: checker.AssetDownloader, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.label.setText(self.tr('Extraindo atualização'))

        # get pyinstaller specific parameter
        self.installation_path = current_path()       # pylint: disable=E1101

        self.downloader = downloader
        self.downloader.done.connect(self._on_download_done)
        self.download_loading = AssetDownloadLoading(self.downloader)

        self.extract_loading = util.LoadingPoints(self.loading_label)
        self.extract_loading.done.connect(self.close)

        self.extraction_runner = util.GenericCallbackRunner(self._extract_update)
        # self.extraction_runner.err.connect(self._o)
        self.extraction_runner.done.connect(self._on_extraction_done)

    def download_and_extract(self):
        self.downloader.start()
        self.download_loading.exec_()

    def _on_download_done(self):
        self.download_loading.close()
        self.extract_loading.start()
        self.extraction_runner.start()
        self.exec_()

    def _on_extraction_done(self, tmpdir):
        self.extract_loading.do_stop.emit()

        # get the first item in the directory, it should be our 
        # application
        main_directory = os.listdir(tmpdir)[0]
        update_path = os.path.join(tmpdir, main_directory)

        # we will assume the same executable of the current one
        main_executable = get_executable(path=update_path)

        # make sure it knows to update
        context.update_config({UPDATER_KEY: self.installation_path})

        # launch updater
        os.startfile(main_executable)       # pylint: disable=E1101

        # exit from old app
        context.exit()

    def _extract_update(self):
        tmpdir = tempfile.mkdtemp()

        # extract everything under a temporary directory
        with zipfile.ZipFile(self.downloader.filepath) as zip:
            zip.extractall(tmpdir)

        return tmpdir


class WindowsUpdateApplier(QtWidgets.QDialog, screen.Ui_Dialog):
    def __init__(self, installation_path, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.label.setText(self.tr('Atualizando'))

        self.installation_path = installation_path

        self.update_loading = util.LoadingPoints(self.loading_label)
        self.update_loading.done.connect(self.close)

        self.update_runner = util.GenericCallbackRunner(self._apply_update)
        # self.update_runner.err.connect(self._on_update_error)
        self.update_runner.done.connect(self._on_update_done)

    def update(self):
        self.update_loading.start()
        self.update_runner.start()
        self.exec_()
        
    def _apply_update(self):
        # move extracted contents into the installation directory
        shutil.copytree(current_path(),     # pylint: disable=E1123
                        self.installation_path,
                        dirs_exist_ok=True)

    def _on_update_done(self):
        self.update_loading.do_stop.emit()
        util.show_dialog(texts.windows_autoupdate_finished)

        # assign that there is no need for updates anymore
        # it should be called before calling the original app
        context.update_config({UPDATER_KEY: None})

        # get the executable from original app
        main_executable = get_executable(path=self.installation_path)

        # re-launches the original app
        os.startfile(main_executable)       # pylint: disable=E1101

        # exit from updater application
        context.exit(0)

    def _on_update_error(self, exc):
        self.update_loading.do_stop.emit()
        util.show_dialog(str(exc))