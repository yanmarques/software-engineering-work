from . import texts
from .. import settings
from ... import widgets
from PyQt5 import QtCore

import platform

default_settings = {
    'check_updates_on_open': True,
    'use_unstable_updates': False,
}


class UpdateSettingsTab(settings.screen.GenericTab):
    def config(self):
        return [
            CheckUpdatesOnOpenSetting,
            UseUnstableUpdatesSetting
        ]


class CheckUpdatesOnOpenSetting(settings.SettingProvider):
    def fields(self):
        return (self.label('buscar novas versões ao abrir'),
                self.checkbox(self.update, self.current_value))

    @property
    def provides(self):
        return 'check_updates_on_open'


class UseUnstableUpdatesSetting(settings.SettingProvider):
    def fields(self):
        return (self.label('usar versões de desenvolvimento'),
                self.checkbox(self._on_state_changed, 
                              self.current_value))

    def _on_state_changed(self, state):
        if state:
            you_sure = widgets.ConfirmationMessageBox()
            text = you_sure.tr(texts.confirm_using_unstable_updates)
            you_sure.setText(text)

            if you_sure.is_accepted():
                # accept the update event
                self.update(state)
            else:
                # reject event and reset the checkbox
                self.rebuild()
        else:
            self.update(state)

    @property
    def provides(self):
        return 'use_unstable_updates'

