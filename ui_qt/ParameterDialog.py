# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math
import datetime

current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '..'))

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QFrame, QLabel, QPushButton, QGridLayout, QSizePolicy, QDateEdit)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont, QPalette, QFontMetrics, QFont

import defs_pars
from ParametersManager import ParametersManager
from Parameter import *

from pyLibQtTools.Tools import SimpleTextEditDialog


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
        super().accept()
        return

    def initialize(self,
                   title):
        if not self.parameter_label in self.parameters_manager.parameters:
            str_error = ('Parameter: {} not found in parameters manager'.format(self.parameter_label))
            return
        self.parameter = self.parameters_manager.parameters[self.parameter_label]
        parameter_label = self.parameter.label
        title = title + parameter_label
        self.setWindowTitle(title)

        grid_layout = QGridLayout()
        # grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        parameter_label = self.parameter.label
        self.label_button = QPushButton(defs_pars.PARAMETER_FIELD_LABEL_TAG)
        self.label_button.clicked.connect(self.set_label)
        self.label_line_edit = QLineEdit()
        self.label_line_edit.setText(parameter_label)
        self.label_line_edit.setReadOnly(True)
        row = 0
        grid_layout.addWidget(self.label_button, row, 0)
        grid_layout.addWidget(self.label_line_edit, row, 1)
        # self.label_line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        parameter_value = str(self.parameter)
        self.value_button = QPushButton(defs_pars.PARAMETER_FIELD_VALUE_TAG)
        self.value_button.clicked.connect(self.set_value)
        self.value_line_edit = QLineEdit()
        self.value_line_edit.setText(parameter_value)
        self.value_line_edit.setReadOnly(True)
        row += 1
        grid_layout.addWidget(self.value_button, row, 0)
        grid_layout.addWidget(self.value_line_edit, row, 1)

        parameter_description = self.parameter.description
        self.description_button = QPushButton(defs_pars.PARAMETER_FIELD_DESCRIPTION_TAG)
        self.description_button.clicked.connect(self.set_description)
        self.description_line_edit = QLineEdit()
        self.description_line_edit.setText(parameter_description)
        self.description_line_edit.setReadOnly(True)
        row += 1
        grid_layout.addWidget(self.description_button, row, 0)
        grid_layout.addWidget(self.description_line_edit, row, 1)

        parameter_output_format = self.parameter.output_format
        self.output_format_button = QPushButton(defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT_TAG)
        self.output_format_button.clicked.connect(self.set_output_format)
        self.output_format_line_edit = QLineEdit()
        self.output_format_line_edit.setText(parameter_output_format)
        self.output_format_line_edit.setReadOnly(True)
        row += 1
        grid_layout.addWidget(self.output_format_button, row, 0)
        grid_layout.addWidget(self.output_format_line_edit, row, 1)

        parameter_argparser = self.parameter.argparser
        self.argparse_button = QPushButton(defs_pars.PARAMETER_FIELD_ARGPARSE_TAG)
        self.argparse_button.clicked.connect(self.set_argparse)
        self.argparse_line_edit = QLineEdit()
        self.argparse_line_edit.setText(parameter_argparser)
        self.argparse_line_edit.setReadOnly(True)
        row += 1
        grid_layout.addWidget(self.argparse_button, row, 0)
        grid_layout.addWidget(self.argparse_line_edit, row, 1)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout((grid_layout))
        vertical_layout.addWidget(self.button_box)

        self.setLayout(vertical_layout)
        # self.label_line_edit.adjustSize()
        # metrics = QFontMetrics(QFont())
        # self.setMinimumWidth(metrics.horizontalAdvance(title))
        # self.setMinimumWidth(200)
        return

    def reject(self):
        super().reject()
        return

    def set_argparse(self):
        title = "Input " + defs_pars.PARAMETER_FIELD_ARGPARSE_TAG
        text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_ARGPARSE_TAG,
                                        QLineEdit.Normal, self.argparse_line_edit.text())
        if ok and text != '' and text != self.argparse_line_edit.text():
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
        if ok and text != '' and text != self.label_line_edit.text():
            self.label_line_edit.setText(text)
        return

    def set_output_format(self):
        title = "Input " + defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT_TAG
        text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT_TAG,
                                        QLineEdit.Normal, self.output_format_line_edit.text())
        if ok and text != '' and text != self.output_format_edit.text():
            self.output_format_line_edit.setText(text)
        return

    def set_value(self):
        title = "Input " + defs_pars.PARAMETER_FIELD_VALUE_TAG
        if isinstance(self.parameter, BooleanParameter):
            items = ['True', 'False']
            current_pos = 0
            if self.value_line_edit.text().casefold() == ('False').casefold():
                current_pos = 1
            item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
            if ok and item:
                self.value_line_edit.setText(item)
        elif isinstance(self.parameter, DateParameter):
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dialog_button_box.accepted.connect(dialog.accept)
            dialog_button_box.rejected.connect(dialog.reject)
            layout = QVBoxLayout()
            message = QLabel("Input a date")
            layout.addWidget(message)
            str_parameter_date = self.value_line_edit.text()
            parameter_date = datetime.datetime.strptime(str_parameter_date, self.parameter.date_format).date()
            # parameter_date = self.parameter.value
            parameter_date_year = parameter_date.year
            parameter_date_month = parameter_date.month
            parameter_date_day = parameter_date.day
            qdate = QDate()
            qdate.setDate(parameter_date_year, parameter_date_month, parameter_date_day)
            dialog_date = QDateEdit(qdate, dialog)
            layout.addWidget(dialog_date)
            layout.addWidget(dialog_button_box)
            dialog.setLayout(layout)
            dialog_result = dialog.exec()
            if dialog_result == QDialog.Accepted:
                new_qdate = dialog_date.date()
                new_year = new_qdate.year()
                new_month = new_qdate.month()
                new_day = new_qdate.day()
                new_date = datetime.date(new_year, new_month, new_day)
                self.parameter.value = new_date
                str_value = str(self.parameter)
                self.value_line_edit.setText(str_value)
        elif isinstance(self.parameter, FileParameter):
            previous_file = self.value_line_edit.text()
            path = QDir.currentPath()
            if os.path.isfile(previous_file):
                path = os.path.dirname(previous_file)
            str_files = '(*.*)'
            if self.parameter.domain:
                str_files = 'Files ('
                for i in range(len(self.parameter.domain)):
                    if i > 0:
                        str_files += ' '
                    str_files += ("*" + self.parameter.domain[i])
                str_files += ')'
            file_name = None
            if self.parameter.file_mode == defs_pars.FILE_MODE_READ:
                file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            elif self.parameter.file_mode == defs_pars.FILE_MODE_APPEND:
                file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            elif self.parameter.file_mode == defs_pars.FILE_MODE_WRITE:
                file_name, aux = QFileDialog.getSaveFileName(self, title, path, str_files)
            if file_name and file_name.casefold() != previous_file.casefold():
                str_value = file_name
                self.value_line_edit.setText(str_value)
            # dlg = QFileDialog()
            # # dlg.setDirectory(self.last_path)
            # if self.parameter.file_mode == defs_pars.FILE_MODE_READ:
            #     dlg.setFileMode(QFileDialog.AnyFile)
            # elif self.parameter.file_mode == defs_pars.FILE_MODE_READ:
            #     dlg.setFileMode(QFileDialog.AnyFile)
            # elif self.parameter.file_mode == defs_pars.FILE_MODE_WRITE:
            #     dlg.setFileMode(QFileDialog.AnyFile)
            # if self.parameter.domain:
            #     str_files = '('
            #     str_files = ')'
            #     dlg.setNameFilter(str_files)
            # if dlg.exec_():
            #     file_names = dlg.selectedFiles()
            #     file_name = file_names[0]
            # else:
            #     return
        elif isinstance(self.parameter, IntegerParameter):
            current_value = int(self.value_line_edit.text())
            domain = self.parameter.domain
            if len(domain) == 2:
                int_value, ok = QInputDialog.getInt(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                           current_value, domain[0], domain[1], 1)
                if ok:
                    str_value = str(eval(self.parameter.output_format.format(int_value)))
                    self.value_line_edit.setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value = str(eval(self.parameter.output_format.format(domain[i])))
                    items.append(str_value)
                current_pos = 0
                if self.value_line_edit.text() in items:
                    current_pos = items.index(self.value_line_edit.text())
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
                if ok and item:
                    self.value_line_edit.setText(item)
        elif isinstance(self.parameter, PhysicalQuantityParameter):
            str_values = self.value_line_edit.text().split()
            str_value = str_values[0]
            current_value = float(str_value)
            domain = self.parameter.domain
            str_unit = ''
            if self.parameter.output_format_unit:
                str_unit = self.parameter.output_format_unit.format(self.parameter.quantity.units)
            if len(domain) == 2:
                str_min_value = str(eval(self.parameter.output_format.format(domain[0])))
                if str_unit:
                    str_min_value += " " + str_unit
                str_max_value = str(eval(self.parameter.output_format.format(domain[1])))
                if self.parameter.output_format_unit:
                    str_max_value += " " + str_unit
                msg = ("Input a value in domain: [{}, {}]:".format( str_min_value, str_max_value))
                text, ok = QInputDialog.getText(self, title, msg,
                                                QLineEdit.Normal, str_value)
                if ok:
                    real_value = None
                    try:
                        real_value = float(text)
                    except ValueError:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        return
                    if real_value < domain[0] or real_value > domain[1]:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        return
                    str_value = str(eval(self.parameter.output_format.format(real_value)))
                    if str_unit:
                        str_value += " " + str_unit
                    self.value_line_edit.setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value = str(eval(self.parameter.output_format.format(domain[i])))
                    if str_unit:
                        str_value += " " + str_unit
                    items.append(str_value)
                current_pos = 0
                if self.value_line_edit.text() in items:
                    current_pos = items.index(self.value_line_edit.text())
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items,
                                                current_pos, False)
                if ok and item:
                    self.value_line_edit.setText(item)
        elif isinstance(self.parameter, RealParameter):
            current_value = float(self.value_line_edit.text())
            domain = self.parameter.domain
            if len(domain) == 2:
                str_min_value = str(eval(self.parameter.output_format.format(domain[0])))
                str_max_value = str(eval(self.parameter.output_format.format(domain[1])))
                msg = ("Input a value in domain: [{}, {}]:".format(str_min_value, str_max_value))
                text, ok = QInputDialog.getText(self, title, msg,
                                                QLineEdit.Normal, self.value_line_edit.text())
                if ok:
                    real_value = None
                    try:
                        real_value = float(text)
                    except ValueError:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        return
                    if real_value < domain[0] or real_value > domain[1]:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        return
                    str_value = str(eval(self.parameter.output_format.format(real_value)))
                    self.value_line_edit.setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value = str(eval(self.parameter.output_format.format(domain[i])))
                    items.append(str_value)
                current_pos = 0
                if self.value_line_edit.text() in items:
                    current_pos = items.index(self.value_line_edit.text())
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items,
                                                current_pos, False)
                if ok and item:
                    self.value_line_edit.setText(item)
        elif isinstance(self.parameter, StringParameter):
            str_value = self.value_line_edit.text()
            if not self.parameter.domain:
                text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                QLineEdit.Normal, str_value)
                if ok and text != '' and text != str_value:
                    self.value_line_edit.setText(text)
            else:
                items = []
                for i in range(len(self.parameter.domain)):
                    str_value_aux = self.parameter.domain[i]
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value)
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
                if ok and item:
                    self.value_line_edit.setText(item)
        else:
            text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                            QLineEdit.Normal, self.value_line_edit.text())
            if ok and text != '' and text != self.output_format_edit.text():
                self.value_line_edit.setText(text)
        return

