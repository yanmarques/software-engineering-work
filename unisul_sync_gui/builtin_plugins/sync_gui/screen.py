from PyQt5 import (
    QtWidgets, 
    QtCore, 
    QtGui
)


class Ui_Tab(QtWidgets.QWidget):
    def setupUi(self):
        self.setObjectName("tab")
        self.mainGrid = QtWidgets.QGridLayout(self)
        self.mainGrid.setObjectName('mainGrid')
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.subject_listview = QtWidgets.QListView(self)
        # self.subject_listview.setMaximumSize(QtCore.QSize(400, 600))
        self.subject_listview.setObjectName("subject_listview")
        self.subject_listview_model = QtGui.QStandardItemModel(self.subject_listview)
        self.subject_listview.setModel(self.subject_listview_model)
        self.gridLayout.addWidget(self.subject_listview, 1, 0, 1, 1)
        self.book_listview = QtWidgets.QListView(self)
        # self.book_listview.setMaximumSize(QtCore.QSize(400, 600))
        self.book_listview.setObjectName("book_listview")
        self.book_listview_model = QtGui.QStandardItemModel(self.book_listview)
        self.book_listview.setModel(self.book_listview_model)
        self.gridLayout.addWidget(self.book_listview, 1, 1, 1, 1)
        # self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        # self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.refresh_button = QtWidgets.QPushButton(self)
        refresh_button_fallback_icon = self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        self.refresh_button.setIcon(QtGui.QIcon.fromTheme('view-refresh', 
                                                          refresh_button_fallback_icon))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(35)
        self.refresh_button.setFont(font)
        self.refresh_button.setObjectName("refresh_button")
        self.horizontalLayout.addWidget(self.refresh_button)

        self.sync_button = QtWidgets.QPushButton(self)
        sync_btn_fallback_icon = self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton)
        self.sync_button.setIcon(QtGui.QIcon.fromTheme('document-save', sync_btn_fallback_icon))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(35)
        self.sync_button.setFont(font)
        self.sync_button.setObjectName("sync_button")
        self.horizontalLayout.addWidget(self.sync_button)

        self.mainGrid.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.mainGrid.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.sync_button.setToolTip(_translate("MainWindow", "sincronizar"))
        self.refresh_button.setToolTip(_translate("MainWindow", "atualizar"))