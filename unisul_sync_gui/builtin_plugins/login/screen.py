# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(398, 160)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.login_button = QtWidgets.QPushButton(Dialog)
        self.login_button.setObjectName("login_button")
        self.gridLayout_2.addWidget(self.login_button, 1, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.user_label = QtWidgets.QLabel(Dialog)
        self.user_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.user_label.setObjectName("user_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.user_label)
        self.user_input = QtWidgets.QLineEdit(Dialog)
        self.user_input.setObjectName("user_input")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.user_input)
        self.password_label = QtWidgets.QLabel(Dialog)
        self.password_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.password_label.setObjectName("password_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.password_label)
        self.password_input = QtWidgets.QLineEdit(Dialog)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("")
        self.password_input.setObjectName("password_input")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.password_input)
        self.remember_checkbox = QtWidgets.QCheckBox(Dialog)
        self.remember_checkbox.setObjectName("remember_checkbox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.remember_checkbox)
        self.gridLayout_2.addLayout(self.formLayout, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "UnisulSync | Login"))
        self.login_button.setText(_translate("Dialog", "Entrar"))
        self.user_label.setText(_translate("Dialog", "E-mail"))
        self.password_label.setText(_translate("Dialog", "Senha"))
        self.remember_checkbox.setText(_translate("Dialog", "Lembrar-me"))
