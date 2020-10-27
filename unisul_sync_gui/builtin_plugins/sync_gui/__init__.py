from . import screen, setting, loaders, texts
from .. import util
from ..settings import PluginTab
from ... import config, spider, signals, widgets
from ...dashboard.window import Dashboard
from ...book_bot.spiders import (
    eva_parser,
    sync_spider
)
from ...app import context, cached_property
from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)

import json
import os


class SyncSpiderThread(QtCore.QThread):
    done = QtCore.pyqtSignal()

    def __init__(self, directory, sync_data):
        super().__init__()
        self.directory = directory
        self.sync_data = sync_data

    def run(self):
        settings = {
            'FILES_STORE': self.directory,
            'CUSTOM_BOOKS': self.sync_data
        }

        spider.crawl(sync_spider.BookDownloaderSpider, 
                     settings=settings,
                     timeout=len(self.sync_data) * 30)

        self.done.emit()


class Loading(QtWidgets.QDialog):
    bump = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        vbox = QtWidgets.QVBoxLayout()
        self.prog_bar = QtWidgets.QProgressBar()
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(0)
        self.bump.connect(self._bump_progress)
        vbox.addWidget(self.prog_bar)
        self.setLayout(vbox)

    def _bump_progress(self, increase):
        curr_value = self.prog_bar.value()
        self.prog_bar.setValue(curr_value + increase)


class DocsListing(screen.Ui_Tab):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi()
        self.init()
        context.signals.showing.emit(sender=self)
        context.signals.landed.connect(self.on_landed)

        # use this variable to store threads
        self.subjects_runner, self.books_runner = None, None

        self.show()

        self.post_init()
        context.signals.shown.emit(sender=self)

    def init(self):
        self.subject_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.book_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # control variables
        self.subjects, self.selected_subjects, self.books, self.selected_books, \
            self._current_books_cache = list(), set(), list(), dict(), tuple()

        # signaling
        self.sync_button.clicked.connect(self.on_sync)
        self.refresh_button.clicked.connect(self.on_refresh)
        self.subject_listview.clicked.connect(self.on_subject_selected)
        self.book_listview.clicked.connect(self.on_book_selected)

        key_sequence = QtGui.QKeySequence('Ctrl+A')
        self.select_all_shortcut = QtWidgets.QShortcut(key_sequence, self)
        self.select_all_shortcut.activated.connect(self.on_select_all)

    def on_landed(self):
        def on_load_done():
            if setting.SyncOnOpen.get():
                self.on_sync(None)

            if setting.SyncAllSelectedOnOpen.get():
                self.on_select_all()

        # fetch and handle data
        self.refresh_subjects_and_books(load_done=on_load_done)

    def post_init(self):
        pass

    def on_sync(self, event):
        sync_data = []

        for subject_index, book_indexes in self.selected_books.items():
            # load the subject
            subject = self.subjects[subject_index]

            # filter all books from this subject
            all_books = self._find_books_by_subject(subject)

            # map selected books and add it to data to sync
            selected_books = [all_books[i] for i in book_indexes]
            sync_data.extend(selected_books)

        if not sync_data:
            util.show_dialog(texts.any_book_selected, 
                             icon=QtWidgets.QMessageBox.Warning,
                             parent=self)
            return

        directory = self._sync_target_dir_or_fail()
        if not directory:
            return

        loading = Loading(parent=self)
        context.signals.syncing.emit(loader=loading,        # pylint: disable=E1101
                                     count=len(sync_data))

        def on_done():
            loading.close()
            context.signals.synced.emit()       # pylint: disable=E1101

            util.show_dialog(texts.sync_done,
                             icon=QtWidgets.QMessageBox.Information,
                             parent=self)
            
            self.setDisabled(False)

        thread = SyncSpiderThread(directory, sync_data)
        thread.done.connect(on_done)
        thread.start()

        self.setDisabled(True)
        loading.exec_()

    def on_select_all(self):
        should_select_all = not self.selected_subjects

        # clear all
        self.selected_subjects.clear()
        self.selected_books.clear()

        if should_select_all:
            self.selected_subjects.update(range(len(self.subjects)))
            for index, subject in enumerate(self.subjects):
                all_books = self._find_books_by_subject(subject)
                self.selected_books[index] = set(range(len(all_books)))

        # reload UI
        self._load_subjects()
        self._select_first_subject()

    def on_subject_selected(self, qtindex):
        index = qtindex.row()
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        
        # if modifiers == Qt.ShiftModifier:
        #     if self.subject_long_select is None:
        #         # register a long select
        #         self.subject_long_select = index
        #     else:
        #         self._handle_long_select(index,
        #                                  self.subject_long_select, 
        #                                  self.selected_subjects)
                
        #         # unregister last long select
        #         self.subject_long_select = None

        #         # reload UI
        #         self._load_subjects()
        #         self._load_books()
        
        if modifiers == QtCore.Qt.ControlModifier:
            was_selected = index in self.selected_subjects

            # unselect when selected
            if was_selected:
                self.selected_subjects.remove(index)

                # unselect all books
                self.selected_books[index] = set()
            else:
                # select this subject
                self.selected_subjects.add(index)

                # go ahead and register the new subject in focus
                self.last_subject_index = index
            
            # reload subject list
            self._load_subjects()

            if self.last_subject_index is None:
                self.last_subject_index = index
            
            # show the last subject
            self._show_subject(self.last_subject_index, select_all=not was_selected)
        else:
            self._show_subject(index)

    def on_book_selected(self, qtindex):
        index = qtindex.row()
        # modifiers = QApplication.keyboardModifiers()
        
        # get the books set of current subject 
        selected_books = self._current_selected_books

        requires_books_reload = True

        # if modifiers == Qt.ShiftModifier:
        #     if self.book_long_select is None:
        #         # register a long select
        #         self.book_long_select = index
        #         requires_books_reload = False
        #     else:
        #         self._handle_long_select(index,
        #                                  self.book_long_select,
        #                                  selected_books)
                
        #         # unregister last long select
        #         self.book_long_select = None
        # else:
        # control wheter subject needs a reload
        requires_subject_reload = False

        if index in selected_books:
            selected_books.remove(index)

            # ensure we unselect the subject when any books selected anymore 
            if not selected_books and self.last_subject_index in self.selected_subjects:
                self.selected_subjects.remove(self.last_subject_index)  
                requires_subject_reload = True  
        else: 
            selected_books.add(index)

            # ensure we select the subject when a book is selected
            self.selected_subjects.add(self.last_subject_index)
            requires_subject_reload = True

        # reload subject UI stuff
        if requires_subject_reload:
            self._load_subjects()

        # reload UI
        if requires_books_reload:    
            self._load_books()

    def on_refresh(self, event):
        # force refresh, user rules
        self.refresh_subjects_and_books(force=True)

    @property
    def _current_selected_books(self):
        # ensure we got a set here
        if self.last_subject_index not in self.selected_books:
            self.selected_books[self.last_subject_index] = set()

        return self.selected_books[self.last_subject_index]

    def _sync_target_dir_or_fail(self):
        dir_from_cfg = setting.SyncDir.get()

        target_dir = dir_from_cfg or self._open_sync_target_dir()
        
        if target_dir:
            setting.SyncDir.update(target_dir)
            if not dir_from_cfg:
                util.show_dialog(texts.first_sync_dir_selected.format(target_dir),
                                 icon=QtWidgets.QMessageBox.Information,
                                 parent=self)
        else:
            util.show_dialog(texts.any_directory_selected,
                             icon=QtWidgets.QMessageBox.Warning,
                             parent=self)

        return target_dir

    def _open_sync_target_dir(self):
        self._maybe_show_choosing_dialog()

        return util.select_directory(parent=self)

    @config.just_once
    def _maybe_show_choosing_dialog(self):
        util.show_dialog(texts.selecting_first_sync_dir,
                         icon=QtWidgets.QMessageBox.Information,
                         parent=self)

    def _handle_long_select(self, current_index, last_index, data_list: set):
        rargs = [last_index, current_index]

        # are we backforwarding
        if current_index < last_index:
            rargs = [current_index, last_index]

        # this index must be inclusive
        rargs[1] += 1

        # binary insert
        for index in range(*rargs):
            if index in data_list:
                data_list.remove(index)
            else:
                data_list.add(index)
        
    def refresh_subjects_and_books(self, load_done=None, **kwargs):
        def on_books_done(books):
            self.books = books
            self.book_listview.setDisabled(False)
            self.subject_listview.setDisabled(False)

            if load_done:
                load_done()

        def on_subjects_done(subjects):
            self.subjects = subjects
            self._load_subjects()
            self.books_runner = util.GenericCallbackRunner(loaders.load_books, 
                                                           **kwargs)
            self.books_runner.done.connect(on_books_done)
            self.books_runner.start()

        self.subject_listview.setDisabled(True)
        self.book_listview.setDisabled(True)
        self.subjects_runner = util.GenericCallbackRunner(loaders.load_subjects, 
                                                          **kwargs)
        self.subjects_runner.done.connect(on_subjects_done)
        self.subjects_runner.start()

    def _select_first_subject(self):
        if not self.subjects:
            return
        self._show_subject(0)

    def _show_subject(self, index, select_all=False):
        self.last_subject_index = int(index)
        
        # get all books of this subject
        subject = self.subjects[self.last_subject_index]
        self._current_books_cache = self._find_books_by_subject(subject)
        
        if select_all:
            all_indexes = range(len(self._current_books_cache))
            self._current_selected_books.update(all_indexes)
        
        self._load_books()

    def _find_books_by_subject(self, subject):
        return [book for book in self.books 
                if book['subject']['class_id'] == subject['class_id']]

    def _load_books(self):
        # remove old books
        self.book_listview_model.clear()

        selected_books = self._current_selected_books

        # load new books into list
        for index, book in enumerate(self._current_books_cache):
            item = QtGui.QStandardItem()
            if index in selected_books:
                item.setCheckState(QtCore.Qt.Checked)
            item.setText(book['name'])
            item.setToolTip(book['filename'])
            self.book_listview_model.appendRow(item)


    def _load_subjects(self):
        self.subject_listview_model.clear()
        for index, subj in enumerate(self.subjects):
            item = QtGui.QStandardItem()
            if index in self.selected_subjects:
                item.setCheckState(QtCore.Qt.Checked)
            item.setText(subj['name'])
            item.setToolTip(subj['class_id'])
            self.subject_listview_model.appendRow(item)


class SyncWizard:
    def __init__(self):
        self.parts = [
            texts.wizard_part1,
            texts.wizard_part2,
            texts.wizard_part3,
        ]

        self.cfg_parts = [ 
            (self._on_sync_on_open_cfg, texts.wizard_cfg_sync_on_open),
            (self._on_sync_all_selected_on_open_cfg, texts.wizard_cfg_all_selected_on_open),
        ]
        self.title = 'UnisuSync | Sync Wizard'

    def start(self):
        for index, text in enumerate(self.parts):
            self._show_part(index, text)
        index += 1
        for cfg_index, (callback, text) in enumerate(self.cfg_parts):
            self._show_cfg(cfg_index + index, callback, text)

    def _show_cfg(self, index, callback, text):
        dialog = widgets.ConfirmationMessageBox()
        window_title = self._build_title(index)
        dialog.setWindowTitle(dialog.tr(window_title))
        dialog.setText(dialog.tr(text))
        callback(dialog.is_accepted())

    def _show_part(self, index, text):
        dialog = QtWidgets.QMessageBox()
        window_title = self._build_title(index)
        dialog.setWindowTitle(dialog.tr(window_title))
        dialog.setText(dialog.tr(text))

        button = QtWidgets.QPushButton()

        if index == len(self.parts) - 1:
            btn_icon = QtWidgets.QStyle.SP_DialogApplyButton
            btn_text = 'Começar'
        else:
            btn_icon = QtWidgets.QStyle.SP_DialogOkButton
            btn_text = 'Próximo'

        button.setIcon(button.style().standardIcon(btn_icon))
        button.setText(button.tr(btn_text))

        dialog.addButton(button, QtWidgets.QMessageBox.AcceptRole)
        dialog.exec_()

    def _on_sync_all_selected_on_open_cfg(self, state):
        setting.SyncAllSelectedOnOpen.update(state)

    def _on_sync_on_open_cfg(self, state):
        setting.SyncOnOpen.update(state)

    def _build_title(self, index):
        total = len(self.parts) + len(self.cfg_parts)
        return f'{self.title} Parte {index + 1}/{total}'


class SyncGuiPlugin(util.PluginDispatch, PluginTab):
    def init(self):
        context.signals.landing.connect(self.on_landing)
        context.signals.landed.connect(self.on_landed)
        config.fix_config(setting.default_settings)

    def signals(self):
        return [
            'item_completed',
            'syncing',
            'synced',
        ]

    def setting_tab(self):
        return ('Sync', setting.SyncTab())

    def on_landing(self, sender=None):
        assert sender is not None
        self._add_dashboard_tab(sender)

    def on_landed(self, sender=None):
        self._maybe_start_wizard()

    def _add_dashboard_tab(self, dashboard: Dashboard):
        tab_widget = dashboard.tabWidget
        self.add_tab(tab_widget, 'Midiateca', DocsListing())

    @config.just_once
    def _maybe_start_wizard(self):
        SyncWizard().start()


plugin = SyncGuiPlugin