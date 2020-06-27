# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_screen.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(470, 163)
        self.user_input = QtWidgets.QLineEdit(Dialog)
        self.user_input.setGeometry(QtCore.QRect(90, 30, 231, 22))
        self.user_input.setObjectName("user_input")
        self.password_input = QtWidgets.QLineEdit(Dialog)
        self.password_input.setGeometry(QtCore.QRect(90, 60, 231, 22))
        self.password_input.setObjectName("password_input")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.user_label = QtWidgets.QLabel(Dialog)
        self.user_label.setGeometry(QtCore.QRect(30, 30, 55, 16))
        self.user_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.user_label.setObjectName("user_label")
        self.password_label = QtWidgets.QLabel(Dialog)
        self.password_label.setGeometry(QtCore.QRect(30, 60, 55, 16))
        self.password_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.password_label.setObjectName("password_label")
        self.remember_checkbox = QtWidgets.QCheckBox(Dialog)
        self.remember_checkbox.setGeometry(QtCore.QRect(90, 90, 100, 20))
        self.remember_checkbox.setObjectName("remember_checkbox")
        self.login_button = QtWidgets.QPushButton(Dialog)
        self.login_button.setGeometry(QtCore.QRect(330, 30, 93, 51))
        self.login_button.setObjectName("login_button")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.user_label.setText(_translate("Dialog", "Usuario"))
        self.password_label.setText(_translate("Dialog", "Senha"))
        self.remember_checkbox.setText(_translate("Dialog", "Lembrar-me"))
        self.login_button.setText(_translate("Dialog", "Entrar"))

