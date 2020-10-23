from PyQt5 import (
    QtWidgets, 
    QtCore, 
    QtGui
)


class Ui_Tab(QtWidgets.QWidget):
    def setupUi(self):
        self.setObjectName("tab")
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayoutWidget = QtWidgets.QWidget(self)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 90, 551, 431))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.subject_listview = QtWidgets.QListView(self.gridLayoutWidget)
        self.subject_listview.setMaximumSize(QtCore.QSize(400, 600))
        self.subject_listview.setObjectName("subject_listview")
        self.subject_listview_model = QtGui.QStandardItemModel(self.subject_listview)
        self.subject_listview.setModel(self.subject_listview_model)
        self.gridLayout.addWidget(self.subject_listview, 0, 0, 1, 1)
        self.book_listview = QtWidgets.QListView(self.gridLayoutWidget)
        self.book_listview.setMaximumSize(QtCore.QSize(400, 600))
        self.book_listview.setObjectName("book_listview")
        self.book_listview_model = QtGui.QStandardItemModel(self.book_listview)
        self.book_listview.setModel(self.book_listview_model)
        self.gridLayout.addWidget(self.book_listview, 0, 1, 1, 1)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 551, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sync_button = QtWidgets.QToolButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.sync_button.setFont(font)
        self.sync_button.setObjectName("sync_button")
        self.horizontalLayout.addWidget(self.sync_button)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.sync_button.setText(_translate("MainWindow", "sincronizar"))