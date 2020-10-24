from ..util import select_directory
from ..settings import screen
from ...app import context
from PyQt5.QtWidgets import QHBoxLayout, QWidget


default_settings = {
    'sync_on_open': True,
    'sync_all_selected_on_open': True,
    'sync_dir': None
}


class SyncTab(screen.GenericTab):
    def config(self):
        return [
            self.sync_on_open(),
            self.sync_all_selected_on_open(),
            self.sync_dir(),
        ]

    def sync_on_open(self):
        def on_change(state):
            context.update_config({'sync_on_open': state})

        return (self.label('sincronizar ao abrir'),
                self.checkbox(on_change, context.config['sync_on_open']))

    def sync_dir(self):
        def on_click():
            directory = select_directory(self)
            if directory:
                context.update_config({'sync_dir': directory})
                self.rebuild()

        path = context.config['sync_dir']
        if path:
            widget = QWidget(self)
            horizontal_layout = QHBoxLayout(widget)
            horizontal_layout.setContentsMargins(0, 0, 0, 0)
            horizontal_layout.setSpacing(80)

            horizontal_layout.addWidget(self.label(path, parent=widget))
            horizontal_layout.addWidget(self.button(on_click, 
                                                    'trocar', 
                                                    parent=widget))
        else:
            widget = self.button(on_click, 'escolher')

        return (self.label('diretório de sincronização'), widget)

    def sync_all_selected_on_open(self):
        def on_change(state):
            context.update_config({'sync_all_selected_on_open': state})
        
        return (self.label('selecionar tudo ao abrir'), 
                self.checkbox(on_change, context.config['sync_all_selected_on_open']))