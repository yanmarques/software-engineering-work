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
        Dialog.resize(406, 212)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 391, 181))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.name = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.name.setMinimumSize(QtCore.QSize(0, 0))
        self.name.setMaximumSize(QtCore.QSize(16777215, 80))
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.verticalLayout.addWidget(self.name, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.version = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.version.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setUnderline(False)
        self.version.setFont(font)
        self.version.setObjectName("version")
        self.verticalLayout_2.addWidget(self.version, 0, QtCore.Qt.AlignHCenter)
        self.author = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.author.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setUnderline(False)
        self.author.setFont(font)
        self.author.setObjectName("author")
        self.verticalLayout_2.addWidget(self.author, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.name.setText(_translate("Dialog", "TextLabel"))
        self.version.setText(_translate("Dialog", "v0.0.0"))
        self.author.setText(_translate("Dialog", "Autor"))
