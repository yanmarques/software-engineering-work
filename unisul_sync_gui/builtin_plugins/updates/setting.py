from .. import settings

default_settings = {
    'check_updates_on_open': True, 
}


class UpdateSettingsTab(settings.screen.GenericTab):
    def config(self):
        return [
            CheckUpdatesOnOpenSetting
        ]


class CheckUpdatesOnOpenSetting(settings.SettingProvider):
    def fields(self):
        return (self.label('buscar novas versões ao abrir'),
                self.checkbox(self.update, self.current_value))

    @property
    def provides(self):
        return 'check_updates_on_open'
