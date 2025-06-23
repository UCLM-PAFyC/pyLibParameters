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
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt

import defs_pars
from ParametersManager import ParametersManager
from Parameter import *
from .ParameterDialog import ParameterDialog


from .Tools import SimpleTextEditDialog


class ParametersManagerDialog(QDialog):
    """Employee dialog."""

    def __init__(self,
                 parameters_manager,
                 title,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'ParametersManagerDialog.ui'), self)
        # loadUi("lib/InstrumentsDialog.ui", self)
        self.parameters_manager = parameters_manager
        self.last_path = None
        self.title = title
        self.formats = None
        self.initialize(title)

    def initialize(self,
                   title):
        self.setWindowTitle(title)
        headers = defs_pars.parameters_manager_dialog_header
        headers_tooltips = defs_pars.parameters_manager_dialog_tooltip_by_header_tag
        field_by_header = defs_pars.parameters_manager_dialog_field_by_header_tag
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setStyleSheet("QHeaderView::section { color:black; background : lightGray; }")
        for i in range(len(headers)):
            header_item = QTableWidgetItem(headers[i])
            header_tooltip = headers_tooltips[headers[i]]
            header_item.setToolTip(header_tooltip)
            self.tableWidget.setHorizontalHeaderItem(i, header_item)
        self.tableWidget.itemDoubleClicked.connect(self.on_click)
        self.tableWidget.itemClicked.connect(self.on_click)
        self.update_gui()
        return

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def on_click(self, item):
        row = item.row()
        column = item.column()
        current_text = item.text()
        parameter_label =  self.tableWidget.item(row, 0).text()
        label = self.tableWidget.horizontalHeaderItem(column).text()
        tool_tip_text = self.tableWidget.horizontalHeaderItem(column).toolTip()
        dialog = ParameterDialog(self.parameters_manager, parameter_label, self)
        dialog_result = dialog.exec()

        # title = "Parameter: " + parameter_label
        # current_text = label.replace('\n', ' ') + ':\n\n' + current_text
        # dialog = SimpleTextEditDialog(title, current_text, True)
        # ret = dialog.exec()
        # # if ret == QDialog.Accepted:
        # #     text = dialog.get_text()
        # #     self.descriptionLineEdit.setText(text)
        # # text = dialog.get_text()
        # # if text != current_text:
        # #     self.descriptionLineEdit.setText(text)
        return

    def update_gui(self):
        self.tableWidget.setRowCount(0)
        for parameter_label in self.parameters_manager.parameters:
            parameter = self.parameters_manager.parameters[parameter_label]
            parameter_description = parameter.description
            parameter_value = str(parameter)
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            label_item = QTableWidgetItem(parameter_label)
            label_item.setTextAlignment(Qt.AlignCenter)
            column_pos = 0
            self.tableWidget.setItem(rowPosition, column_pos, label_item)
            value_item = QTableWidgetItem(parameter_value)
            value_item.setTextAlignment(Qt.AlignCenter)
            column_pos += 1
            self.tableWidget.setItem(rowPosition, column_pos, value_item)
            description_item = QTableWidgetItem(parameter_description)
            description_item.setTextAlignment(Qt.AlignCenter)
            column_pos += 1
            self.tableWidget.setItem(rowPosition, column_pos, description_item)
        self.tableWidget.resizeColumnsToContents()


