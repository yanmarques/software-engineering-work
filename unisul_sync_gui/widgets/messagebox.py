from PyQt5 import QtWidgets, QtGui, QtCore


class ConfirmationMessageBox(QtWidgets.QMessageBox):
    def __init__(self, 
                 accept_text='Sim', 
                 reject_text='Não',
                 default_accept=True,
                 parent=None):
        super().__init__(parent=parent)
        accept_style = QtWidgets.QStyle.SP_DialogApplyButton
        accept_button = self.custom_button(accept_text, accept_style)
        self.addButton(accept_button, QtWidgets.QMessageBox.AcceptRole)

        reject_style = QtWidgets.QStyle.SP_DialogCancelButton
        reject_button = self.custom_button(reject_text, reject_style)
        self.addButton(reject_button, QtWidgets.QMessageBox.RejectRole)

        default_button = accept_button if default_accept else reject_button
        self.setDefaultButton(default_button)

    def is_accepted(self):
        return self.exec_() == 0

    def custom_button(self, text, icon):
        button = QtWidgets.QPushButton(self)
        button.setText(self.tr(text))
        button.setIcon(self.custom_icon(icon))
        return button

    def custom_icon(self, std_icon):
        return self.style().standardIcon(std_icon)