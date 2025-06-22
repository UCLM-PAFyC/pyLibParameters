# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math

current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '..'))

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QFrame, QLabel, QPushButton, QGridLayout)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont, QPalette

import defs_pars
from ParametersManager import ParametersManager
from Parameter import *


from .Tools import SimpleTextEditDialog


class ParameterDialog(QDialog):
    def __init__(self,
                 parameters_manager,
                 parameter_label,
                 parent = None):
        super().__init__(parent)
        self.parameters_manager = parameters_manager
        self.parameter_label = parameter_label
        title = "Parameter: "
        self.initialize(title)
        self.str_error = ""

    def accept(self):
        yo = 1
        super().accept()
        return

    def initialize(self,
                   title):
        self.setWindowTitle(title)

        # frameStyle = QFrame.Sunken | QFrame.Panel

        if not self.parameter_label in self.parameters_manager.parameters:
            str_error = ('Parameter: {} not found in parameters manager'.format(self.parameter_label))
            return
        self.parameter = self.parameters_manager.parameters[self.parameter_label]

        parameter_label = self.parameter.label
        self.label_button = QPushButton(defs_pars.PARAMETER_FIELD_LABEL_TAG)
        self.label_button.clicked.connect(self.set_label)
        self.label_line_edit = QLineEdit()
        self.label_line_edit.setText(parameter_label)
        self.label_line_edit.setReadOnly(True)

        parameter_argparser = self.parameter.argparser
        self.argparse_button = QPushButton(defs_pars.PARAMETER_FIELD_ARGPARSE_TAG)
        self.argparse_button.clicked.connect(self.set_argparse)
        self.argparse_line_edit = QLineEdit()
        self.argparse_line_edit.setText(parameter_argparser)
        self.argparse_line_edit.setReadOnly(True)

        parameter_description = self.parameter.description
        self.description_button = QPushButton(defs_pars.PARAMETER_FIELD_DESCRIPTION_TAG)
        self.description_button.clicked.connect(self.set_description)
        self.description_line_edit = QLineEdit()
        self.description_line_edit.setText(parameter_description)
        self.description_line_edit.setReadOnly(True)

        # self.description = description
        # self.output_format = output_format
        # self.value = None
        # self.mandatory = mandatory
        # self.enabled = enabled

        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)
        # grid_layout.setColumnMinimumWidth(1, 250)
        row = 0
        grid_layout.addWidget(self.label_button, row, 0)
        grid_layout.addWidget(self.label_line_edit, row, 1)
        row += 1
        grid_layout.addWidget(self.argparse_button, row, 0)
        grid_layout.addWidget(self.argparse_line_edit, row, 1)
        row += 1
        grid_layout.addWidget(self.description_button, row, 0)
        grid_layout.addWidget(self.description_line_edit, row, 1)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout((grid_layout))
        vertical_layout.addWidget(self.button_box)

        self.setLayout(vertical_layout)
        return

    def reject(self):
        yo = 1
        super().reject()
        return

    def set_argparse(self):
        title = "Input " + defs_pars.PARAMETER_FIELD_ARGPARSE_TAG
        text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_ARGPARSE_TAG,
                                        QLineEdit.Normal, self.argparse_line_edit.text())
        if ok and text != '' and text != self.parameter_label:
            self.argparse_line_edit.setText(text)
        return

    def set_description(self):
        title = "Parameter: " + self.label_line_edit.text()
        current_text = self.description_line_edit.text()
        dialog = SimpleTextEditDialog(title, current_text, False)
        ret = dialog.exec()
        text = dialog.get_text()
        if text != self.description_line_edit.text():
            self.description_line_edit.setText(text)
        # if ret == QDialog.Accepted:
        #     text = dialog.get_text()
        #     if text != '' and text != self.description_line_edit.text():
        #         self.description_line_edit.setText(text)
        return

    def set_label(self):
        title = "Input " + defs_pars.PARAMETER_FIELD_LABEL_TAG
        text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_LABEL_TAG,
                                        QLineEdit.Normal, self.argparse_line_edit.text())
        if ok and text != '' and text != self.parameter_label:
            self.label_line_edit.setText(text)
        return
