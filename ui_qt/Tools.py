# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize

class SimpleTextEditDialog(QDialog):
    def __init__(self,
                 title,
                 text,
                 readOnly):
        super().__init__()
        # QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        # self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.ptd = QPlainTextEdit(self)
        self.ptd.setReadOnly(readOnly)
        # self.ptd.setEnabled(False)
        layout.addWidget(self.ptd)
        # layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle(title)
        self.ptd.insertPlainText(text)

    def get_text(self):
        return self.ptd.toPlainText()


def error_msg(str_msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setWindowTitle('Error:')
    msgBox.setText(str_msg)
    # msgBox.setInformativeText("Do you want to save your changes?")
    # msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    # msgBox.setDefaultButton(QMessageBox.Save)
    ret = msgBox.exec()


def warning_msg(str_msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setWindowTitle('Warning:')
    msgBox.setText(str_msg)
    # msgBox.setInformativeText("Do you want to save your changes?")
    # msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    # msgBox.setDefaultButton(QMessageBox.Save)
    ret = msgBox.exec()


def info_msg(str_msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setWindowTitle('Information:')
    msgBox.setText(str_msg)
    # msgBox.setInformativeText("Do you want to save your changes?")
    # msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    # msgBox.setDefaultButton(QMessageBox.Save)
    ret = msgBox.exec()
