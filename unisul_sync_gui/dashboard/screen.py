# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unisul_sync_gui/sync/interface.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 625)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.opts_menu = QtWidgets.QMenu(self.menubar)
        self.opts_menu.setObjectName("opts_menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.logout_button = QtWidgets.QAction(MainWindow)
        self.logout_button.setObjectName("logout_button")
        self.logout_button.setIcon(QtGui.QIcon.fromTheme('system-log-out'))
        self.close_button = QtWidgets.QAction(MainWindow)
        self.close_button.setObjectName("close_button")
        self.close_button.setIcon(QtGui.QIcon.fromTheme('application-exit'))

        self.menubar.addAction(self.opts_menu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "UnisulSync | Dashboard"))
        self.opts_menu.setTitle(_translate("MainWindow", "Opções"))
        self.logout_button.setText(_translate("MainWindow", "Logout"))
        self.close_button.setText(_translate("MainWindow", "Fechar"))
