from . import setting, checker, screen, texts
from .. import util, help
from ..settings import PluginTab
from ... import config, widgets
from ...app import context
from PyQt5 import QtWidgets, QtCore, QtGui

import distro
import webbrowser


class DownloadManager:
    def __init__(self, downloader: checker.AssetDownloader):
        self.downloader = downloader
        self.size, self.per_chunk, self.progress = 0, 0, 0
        self.downloader.got_response.connect(self._gather_initial_info)
        self.downloader.chunk_wrote.connect(self._bump)
        self.downloader.done.connect(self._done)

    def start(self):
        self.downloader.download()

    def _gather_initial_info(self, size=None):
        assert size
        self.size = size
        self.per_chunk = (self.downloader.chunk_size * 100) / size
        print(self.per_chunk)
        print(self.progress)

    def _bump(self):
        self.progress += self.per_chunk
        progress = int(self.progress)
        if progress % 10 == 0 or progress % 2 == 0 or progress % 5 == 0:
            print(str(int(self.progress)))

    def _done(self):
        print('DONE')

    
class AssetDownloadLoading(QtWidgets.QDialog):
    init_download = QtCore.pyqtSignal(int)
    bump = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        vbox = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.label.setText(self.tr('Enviando requisição...'))
        vbox.addWidget(self.label)
        self.prog_bar = QtWidgets.QProgressBar()
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(0)
        self.bump.connect(self._bump_progress)
        self.init_download.connect(self._received_response)
        vbox.addWidget(self.prog_bar)
        self.setLayout(vbox)

    def _received_response(self, download_len):
        self.label.setText(self.tr(f'0/{download_len}'))

    def _bump_progress(self, increase):
        curr_value = self.prog_bar.value()
        self.prog_bar.setValue(curr_value + increase)


class UpdateCheckerRunnable(QtCore.QThread):
    done = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.update_checker = checker.UpdateChecker()

    def run(self):
        has_updates = self.update_checker.check()
        self.done.emit(has_updates)


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


class UpdateUserInterface(QtWidgets.QDialog, screen.Ui_Dialog):
    no_updates = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.loading = LoadingPoints(self.loading_label)
        self.loading.done.connect(self.close)
        self.loading.start()

        self.checker_runner = UpdateCheckerRunnable()
        self.checker_runner.done.connect(self._on_update_check)
        self.checker_runner.start()

    def _on_update_check(self, has_updates):
        self.loading.do_stop.emit()

        if has_updates:
            DownloadLatestVersion(self.checker_runner.update_checker)
        else:
            self.no_updates.emit()


class DownloadLatestVersion(widgets.ConfirmationMessageBox):
    def __init__(self, update_checker: checker.UpdateChecker):
        super().__init__(accept_text='Baixar', reject_text='Agora não')
        self.update_checker = update_checker
        text = f'Nova versão disponível: {update_checker.latest_version}'
        self.setText(self.tr(text))

        if self.is_accepted():
            self._handle_download()

    def _handle_download(self):
        asset_name = self._check_system_availability()
        if asset_name is None:
            return

        downloader = self.update_checker.build_downloader(None)
        webbrowser.open(downloader.url)
        self._show_update_instructions(asset_name)
        
        keep_using = widgets.ConfirmationMessageBox(default_accept=False)
        keep_using.setText(texts.keep_using_after_update_downloaded)
        if not keep_using.is_accepted():
            # get the hell out
            context.exit()

    def _show_update_instructions(self, asset_name):
        instructions = {
            checker.WINDOWS_ASSET: texts.windows_update_instructions,
            checker.DEBIAN_ASSET: texts.deb_update_instructions,
            checker.RPM_ASSET: texts.rpm_update_instructions,
        }

        text = instructions[asset_name]
        util.show_dialog(text,
                         icon=QtWidgets.QMessageBox.Information)

    def _check_system_availability(self):
        try:
            return checker.deduce_asset()
        except checker.UnavailableOperatingSystem:
            self._on_unavailable_os()
        except checker.UnavailableLinuxDistribution:
            self._on_unavailable_linux_dist()
       
    def _on_unavailable_os(self):
        self.close()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(msg.tr(texts.unavailable_os))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def _on_unavailable_linux_dist(self):
        self.close()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(msg.tr(texts.unavailable_linux_distribution))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


class UpdatesPlugin(PluginTab):
    def init(self):
        # we can safely connect to this custom signal here
        context.signals.help_menu.connect(self.add_menu_action)     # pylint: disable=E1101

        config.fix_config(setting.default_settings)
        if context.config['check_updates_on_open']:
            UpdateUserInterface().exec_()

    def add_menu_action(self, menu: help.HelpMenu = None):
        check_update_act = QtWidgets.QAction(menu)
        check_update_act.setIcon(QtGui.QIcon.fromTheme('system-software-update'))
        check_update_act.setText('Verificar atualizações')
        check_update_act.triggered.connect(self.check_for_updates)
        menu.addAction(check_update_act)

    def check_for_updates(self):
        update_ui = UpdateUserInterface()
        update_ui.no_updates.connect(self._on_fully_updated)
        update_ui.exec_()
            
    def setting_tab(self):
        return 'Atualizações', setting.UpdateSettingsTab()

    def _on_fully_updated(self):
        util.show_dialog(texts.already_updated)


plugin = UpdatesPlugin