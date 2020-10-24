# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


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


class GenericTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("general_tab")
        self.formLayoutWidget = QtWidgets.QWidget(self)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 581, 351))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(35)
        self.formLayout.setObjectName("formLayout")
        self._build_form()

    def label(self, text, parent=None):
        label = QtWidgets.QLabel(parent=parent or self)
        label.setText(self._translate(text))
        return label

    def checkbox(self, on_change, initial_value=False, parent=None):
        def on_change_wrapper(state):
            value = True if state == QtCore.Qt.Checked else False
            on_change(value)

        checkbox = QtWidgets.QCheckBox(parent=parent or self)
        checkbox.setChecked(initial_value)
        checkbox.stateChanged.connect(on_change_wrapper)
        return checkbox

    def combobox(self, on_change, items, parent=None, tooltips=[]):
        combobox = QtWidgets.QComboBox(parent=parent or self)
        combobox.addItems(items)
        for index, tooltip in enumerate(tooltips):
            combobox.setItemData(index, tooltip, QtCore.Qt.ToolTip)
        combobox.activated.connect(on_change)
        return combobox

    def button(self, on_click, text, parent=None):
        button = QtWidgets.QToolButton(parent=parent or self)
        button.clicked.connect(on_click)
        button.setText(self._translate(text))
        return button

    def config(self):
        return []

    def rebuild(self):
        for _ in range(self.formLayout.rowCount()):
            self.formLayout.removeRow(0)
        self._build_form()

    def _build_form(self):
        for index, (label, field) in enumerate(self.config()):
            self.formLayout.setWidget(index, QtWidgets.QFormLayout.LabelRole, label)
            self.formLayout.setWidget(index, QtWidgets.QFormLayout.FieldRole, field)

    def _translate(self, text):
        return QtCore.QCoreApplication.translate('Dialog', text)
        