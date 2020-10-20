# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'software-engineering-work/list_screen.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1000, 684)
        self.logout_button = QtWidgets.QPushButton(Dialog)
        self.logout_button.setGeometry(QtCore.QRect(900, 20, 91, 28))
        self.logout_button.setObjectName("logout_button")
        self.subject_listview = QtWidgets.QListView(Dialog)
        self.subject_listview.setGeometry(QtCore.QRect(10, 70, 511, 601))
        self.subject_listview.setObjectName("subject_listview")
        self.subject_listview_model = QtGui.QStandardItemModel(self.subject_listview)
        self.subject_listview.setModel(self.subject_listview_model)
        self.sync_button = QtWidgets.QPushButton(Dialog)
        self.sync_button.setGeometry(QtCore.QRect(490, 10, 101, 51))
        self.sync_button.setObjectName("sync_button")
        # self.search_input = QtWidgets.QLineEdit(Dialog)
        # self.search_input.setGeometry(QtCore.QRect(100, 30, 281, 22))
        # self.search_input.setObjectName("search_input")
        # self.search_label = QtWidgets.QLabel(Dialog)
        # self.search_label.setGeometry(QtCore.QRect(20, 30, 71, 16))
        # self.search_label.setObjectName("search_label")
        # self.search_button = QtWidgets.QPushButton(Dialog)
        # self.search_button.setGeometry(QtCore.QRect(390, 30, 50, 24))
        # self.search_button.setObjectName("search_button")
        self.book_listview = QtWidgets.QListView(Dialog)
        self.book_listview.setGeometry(QtCore.QRect(530, 70, 461, 601))
        self.book_listview.setObjectName("book_listview")
        self.book_listview_model = QtGui.QStandardItemModel(self.book_listview)
        self.book_listview.setModel(self.book_listview_model)
        self.select_all = QtWidgets.QPushButton(Dialog)
        self.select_all.setGeometry(QtCore.QRect(610, 30, 140, 21))
        self.select_all.setObjectName("select_all")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Unisul Sync"))
        self.logout_button.setText(_translate("Dialog", "Logout"))
        self.sync_button.setText(_translate("Dialog", "Sincronizar"))
        # self.search_label.setText(_translate("Dialog", "Pesquisar"))
        # self.search_button.setText(_translate("Dialog", "buscar"))
        self.select_all.setText(_translate("Dialog", "(de)selecionar Tudo"))
