from . import screen
from unisul_sync_gui import config, spider
from unisul_sync_gui.app import context, cached_property
from unisul_sync_gui.book_bot.spiders import eva_parser, sync_spider
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QEvent, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QAbstractItemView, 
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QProgressBar,
)

import json
import os


class SpiderThread(QThread):
    done = pyqtSignal()

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


class Loading(QDialog):
    bump = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        vbox = QVBoxLayout()
        self.prog_bar = QProgressBar()
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(0)
        self.bump.connect(self._bump_progress)
        vbox.addWidget(self.prog_bar)
        self.setLayout(vbox)

    def _bump_progress(self, increase):
        curr_value = self.prog_bar.value()
        self.prog_bar.setValue(curr_value + increase)


class Listing(QMainWindow, screen.Ui_Dialog):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.subject_listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.book_listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # control variables
        self.subjects, self.selected_subjects, self.books, self.selected_books, \
            self._current_books_cache = list(), set(), list(), dict(), tuple()
        
        self.subject_long_select, self.book_long_select, self.last_subject_index = None, None, None

        # fetch and handle data
        self._fetch_and_load_subjects()
        self._fetch_books()
        self.on_select_all(None)

        # signaling
        self.subject_listview.clicked.connect(self.on_subject_selected)
        self.book_listview.clicked.connect(self.on_book_selected)
        self.select_all.clicked.connect(self.on_select_all)
        self.sync_button.clicked.connect(self.on_sync)
        self.logout_button.clicked.connect(self.on_logout)

        self.show()
        context.signals.shown.emit(sender=self)
        self.on_sync(None)

    def on_logout(self, event):
        msg = QMessageBox(parent=self)
        msg.setIcon(QMessageBox.Question)
        msg.setText('Tem certeza que deseja sair?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            login = context.windows['login'] 
            
            # actully logout, this invalidates the cookiejar stored in disk
            login.http_auth.logout()

            self.close()

            # reopen a fresh login window, without trying credentials from disk
            # because we do not want to login again
            context.windows['login'] = login.new_from_this(ignore_disk_creds=True)

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
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Nenhum conteúdo selecionado. Por favor tente selecionar pelo menos 1.')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        directory = self._sync_target_dir_or_fail()
        if not directory:
            return

        loading = Loading(parent=self)
        context.signals.syncing.emit(loader=loading,
                                     count=len(sync_data))

        def on_done():
            loading.close()
            context.signals.synced.emit()

            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Sincronização finalizada.')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            self.setDisabled(False)

        thread = SpiderThread(directory, sync_data)
        thread.done.connect(on_done)
        thread.start()

        self.setDisabled(True)
        loading.exec_()

    def on_select_all(self, event):
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
        modifiers = QApplication.keyboardModifiers()
        
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
        
        if modifiers == Qt.ControlModifier:
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

    @property
    def _current_selected_books(self):
        # ensure we got a set here
        if self.last_subject_index not in self.selected_books:
            self.selected_books[self.last_subject_index] = set()

        return self.selected_books[self.last_subject_index]

    def _sync_target_dir_or_fail(self):
        dir_from_cfg = context.config.get('sync_dir')

        if dir_from_cfg:
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Deseja continuar usando este diretório: \n{}'.format(dir_from_cfg))
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            result = msg.exec_()
            if result == QMessageBox.Cancel:
                return

            if result == QMessageBox.No:
                dir_from_cfg = None

        target_dir = dir_from_cfg or self._open_sync_target_dir()
        
        if target_dir:
            context.update_config({'sync_dir': target_dir})
            if not dir_from_cfg:
                msg = QMessageBox(parent=self)
                msg.setIcon(QMessageBox.Information)
                text = 'Vi aqui que você ainda não possui um diretório padrão.\n'
                text += 'Então já me adiantei e salvei o diretório "{}" nas suas configurações.'
                msg.setText(text.format(target_dir))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()    
        else:
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Nenhum diretório para a sincronização selecionado.')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        return target_dir

    def _open_sync_target_dir(self):
        self._maybe_show_choosing_dialog()

        dialog = QFileDialog(parent=self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            if filenames:
                return filenames[0]

    @config.just_once
    def _maybe_show_choosing_dialog(self):
        msg = QMessageBox(parent=self)
        msg.setIcon(QMessageBox.Information)
        msg.setText('Ei, novata (o)!\nAgora você deve escolher aonde deseja salvar os documentos a serem sincronizados.')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

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
        
    def _fetch_books(self):
        exported_file = self._crawler_default_settings['BOOK_EXPORTER_URI']
        self.books = self._fetch_from_spider(eva_parser.BookSpider, 
                                             exported_file)

    def _fetch_and_load_subjects(self):
        exported_file = self._crawler_default_settings['SUBJECT_EXPORTER_URI']
        self.subjects = self._fetch_from_spider(eva_parser.SubjectSpider, exported_file)
        self._load_subjects()

    def _fetch_from_spider(self, spider_cls, exported_file, force_fetch=True):
        exported_path = config.path_name_of(exported_file)

        if force_fetch or not os.path.exists(exported_path):
            settings = {
                'EXPORTER_DIR': config.config_path()
            }

            spider.crawl(spider_cls, settings=settings)

        with open(exported_path, encoding='utf8') as io_reader:
            return json.load(io_reader)

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
            item = QStandardItem()
            if index in selected_books:
                item.setCheckState(Qt.Checked)
            item.setText(book['name'])
            item.setToolTip(book['filename'])
            self.book_listview_model.appendRow(item)


    def _load_subjects(self):
        self.subject_listview_model.clear()
        for index, subj in enumerate(self.subjects):
            item = QStandardItem()
            if index in self.selected_subjects:
                item.setCheckState(Qt.Checked)
            item.setText(subj['name'])
            item.setToolTip(subj['class_id'])
            self.subject_listview_model.appendRow(item)

    @cached_property
    def _crawler_default_settings(self):
        return spider._get_from_project()