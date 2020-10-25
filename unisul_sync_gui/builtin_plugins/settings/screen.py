# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from .. import util
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog, main_tab):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(620, 424)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 601, 401))
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.addTab(main_tab, "")

        self.retranslateUi(Dialog, main_tab)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog, main_tab):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Configurações"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(main_tab), _translate("Dialog", "Geral"))


class GenericTab(util.WidgetBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("genericTab")
        self.formLayoutWidget = QtWidgets.QWidget(self)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 581, 351))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(35)
        self.formLayout.setObjectName("formLayout")
        self.rebuild()

    def config(self) -> list:
        raise NotImplementedError('Missing [config] method to be implemented.')

    def rebuild(self):
        util.clear_layout(self.formLayout)
        self._build_form()

    def _build_form(self):
        for index, provider_class in enumerate(self.config()):
            provider = provider_class(self.formLayoutWidget)
            label, field = provider.fields()
            self.formLayout.setWidget(index, QtWidgets.QFormLayout.LabelRole, label)
            self.formLayout.setWidget(index, QtWidgets.QFormLayout.FieldRole, field)