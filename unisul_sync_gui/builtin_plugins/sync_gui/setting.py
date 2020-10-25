from . import loaders
from .. import util
from ..settings import screen, SettingProvider
from ...app import context
from PyQt5 import QtWidgets

default_settings = {
    'sync_on_open': True,
    'sync_all_selected_on_open': True,
    'sync_dir': None,
    'sync_subject_frequency': None, 
}


class SyncTab(screen.GenericTab):
    def config(self):
        return [
            SyncOnOpen,
            SyncAllSelectedOnOpen,
            SyncDir,
            SyncSubjectFrequency,
        ]
        
        
class SyncOnOpen(SettingProvider):
    def fields(self):
        return (self.label('sincronizar ao abrir'),
                self.checkbox(self.update, self.current_value))

    @property
    def provides(self):
        return 'sync_on_open'


class SyncDir(SettingProvider):
    def init(self):
        self.main_widget = self._widget(QtWidgets.QWidget)
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(80)
        self._add_widgets()

    def fields(self):
        return (self.label('diretório de sincronização'), self.main_widget)

    @property
    def provides(self):
        return 'sync_dir'

    def _add_widgets(self):
        path = self.current_value
        if path:
            path_label = self.label(path, parent=self.main_widget)
            change_button = self.button(self._on_click, 
                                        'trocar', 
                                        parent=self.main_widget)

            self.horizontal_layout.addWidget(path_label)
            self.horizontal_layout.addWidget(change_button)
        else:
            choose_button = self.button(self._on_click, 
                                        'escolher', 
                                        parent=self.main_widget)
            self.horizontal_layout.addWidget(choose_button)

    def _on_click(self):
        directory = util.select_directory()
        if directory:
            self.update(directory)
        
            # rebuild our way
            util.clear_layout(self.horizontal_layout)
            self._add_widgets()


class SyncAllSelectedOnOpen(SettingProvider):
    def fields(self):
        return (self.label('selecionar tudo ao abrir'), 
                self.checkbox(self.update, self.current_value))

    @property
    def provides(self):
        return 'sync_all_selected_on_open'


class SyncSubjectFrequency(SettingProvider):
    def init(self):
        all_preds = loaders.default_predicates.values()
        curr_index = list(all_preds).index(self._predicate)

        predicates, tooltips = [], []
        for pred in loaders.default_predicates.values():
            predicates.append(self._translate(pred.name()))
            tooltips.append(self._translate(pred.description()))

        self._combobox = self.combobox(self._on_change, 
                                       items=predicates,
                                       tooltips=tooltips,
                                       index=curr_index)

    def fields(self):
        return (self.label('frequência de atualização\ndas unidades de aprendizagem'),
                self._combobox)

    @property
    def provides(self):
        return 'sync_subject_frequency'

    @property
    def _predicate(self):
        return loaders.find_available_pred(self.current_value)

    def _on_change(self, index):
        pred_key = list(loaders.default_predicates)[index]
        self.update(pred_key)

        tooltip = self._predicate.description()
        self._combobox.setToolTip(self._translate(tooltip))