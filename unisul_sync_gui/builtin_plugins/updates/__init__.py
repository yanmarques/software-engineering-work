from . import (
    setting, 
    checker, 
    screen, 
    texts,
    autoupdate,
)
from .. import util, help
from ..settings import PluginTab
from ... import config, widgets
from ...app import context
from PyQt5 import QtWidgets, QtCore, QtGui

import platform
import webbrowser


class UpdateCheckerRunnable(QtCore.QThread):
    done = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.update_checker = checker.UpdateChecker()

    def run(self):
        has_updates = self.update_checker.check()
        self.done.emit(has_updates)


class UpdateUserInterface(QtWidgets.QDialog, screen.Ui_Dialog):
    no_updates = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.loading = util.LoadingPoints(self.loading_label)
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

        handlers = {
            'Windows': self._handle_windows_update,
        }

        choose_handler = handlers.get(platform.system(), 
                                      self._handle_common_download)
        choose_handler(checker.WINDOWS_ASSET)

    def _handle_windows_update(self, asset_name):
        # make sure we can auto-update
        if autoupdate.can_make_it():
            autoupdate.make(self.update_checker)
        else:
            do_download = widgets.ConfirmationMessageBox(default_accept=False)
            do_download.setText(texts.windows_not_bundled_on_update)
            if do_download.is_accepted():
                self._handle_common_download(asset_name)
    
    def _handle_common_download(self, asset_name):
        download_url = self.update_checker.build_download_url()
        webbrowser.open(download_url)
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
        util.show_dialog(text.format(asset_name),
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
        if setting.CheckUpdatesOnOpenSetting.get():
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