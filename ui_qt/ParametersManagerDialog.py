# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math

current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '..'))

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog, QHBoxLayout, QDoubleSpinBox,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit, QDateEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate

import defs_pars
from ParametersManager import ParametersManager
from Parameter import *
from .ParameterDialog import ParameterDialog
from ui_qt.VectorLayerFieldDialog import VectorLayerFieldDialog


from .Tools import SimpleTextEditDialog


class ParametersManagerDialog(QDialog):
    """Employee dialog."""

    def __init__(self,
                 parameters_manager,
                 title,
                 qgis_iface,
                 settings,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'ParametersManagerDialog.ui'), self)
        # loadUi("lib/InstrumentsDialog.ui", self)
        self.parameters_manager = parameters_manager
        self.title = title
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.formats = None
        self.quantity_parameter = None
        self.quantity_unit_combo_box = None
        self.quantity_previous_selected_unit = None
        self.quantity_value_edit = None
        self.selected_parameter_label = None
        self.initialize(title)

    def accept(self):
        self.save()
        self.close()
        # self.super().accept()

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
        self.dialogButtonBox.accepted.connect(self.accept)
        self.dialogButtonBox.rejected.connect(self.reject)
        self.update_gui()
        return

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def on_click(self, item):
        row = item.row()
        column = item.column()
        if column != 1:
            return
        current_text = item.text()
        parameter_label =  self.tableWidget.item(row, 0).text()
        label = self.tableWidget.horizontalHeaderItem(column).text()
        tool_tip_text = self.tableWidget.horizontalHeaderItem(column).toolTip()
        self.set_value(row)

        # dialog = ParameterDialog(self.parameters_manager, parameter_label, self)
        # dialog_result = dialog.exec()

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

    def save(self):
        for i in range(self.tableWidget.rowCount()):
            parameter_label = self.tableWidget.item(i, 0).text()
            str_value = self.tableWidget.item(i, 1).text()
            str_error = self.parameters_manager.set_value(parameter_label, str_value)
            if str_error:
                str_error = ('Saving parameter: {}, value: {}\nError: {}\nError:\n{}'.
                             format(parameter_label, str_error))
                QMessageBox.information(self, 'Information', str_value, str_error)
                # return
        # str_msg = ('Saving of parameters has finished')
        # QMessageBox.information(self, 'Information', str_msg)
        return

    def select_quantity_unit(self):
        new_unit = self.quantity_unit_combo_box.currentText()
        if new_unit == self.quantity_previous_selected_unit:
            return
        str_value_previous_unit = self.quantity_value_edit.text()
        value_previous_unit = None
        try:
            value_previous_unit = float(str_value_previous_unit)
        except ValueError:
            msg = ('Value must be a real number')
            # msg = ('Value must be a real number in domain: [{}, {}]'
            #        .format(str_min_value, str_max_value))
            QMessageBox.information(self, 'Information', msg)
            pos = self.quantity_unit_combo_box.findText(self.quantity_previous_selected_unit)
            self.quantity_unit_combo_box.setCurrentIndex(pos)
            return
        quantity_previous_unit = defs_pars.ureg.Quantity
        try:
            quantity_previous_unit = quantity_previous_unit(value_previous_unit, self.quantity_previous_selected_unit)
        except Exception as quantity_error:
            str_error = (
                'Physical Quantity Parameter: {} setting value error:\n{}'.
                format(self.selected_parameter_label, quantity_error))
            QMessageBox.information(self, 'Information', str_error)
            pos = self.quantity_unit_combo_box.findText(self.quantity_previous_selected_unit)
            self.quantity_unit_combo_box.setCurrentIndex(pos)
            return str_error
        quantity_selected_unit = quantity_previous_unit.to(new_unit)
        value_selected_unit = quantity_selected_unit.magnitude
        # if new_ui_value < domain[0] or new_ui_value > domain[1]:
        #     msg = ('Value must be a real number in domain: [{}, {}]'
        #            .format(str_min_value, str_max_value))
        #     QMessageBox.information(self, 'Information', msg)
        #     self.quantity_unit_combo_box.currentIndexChanged.disconnect(select_quantity_unit)
        #     return
        str_value_selected_unit = str(eval(self.quantity_parameter.output_format.format(value_selected_unit)))
        # if str_unit:
        #     str_value += " " + str_unit
        self.quantity_value_edit.setText(str_value_selected_unit)
        self.quantity_previous_selected_unit = new_unit
        return

    def set_value(self, row):
        parameter_label =  self.tableWidget.item(row, 0).text()
        self.selected_parameter_label = parameter_label
        str_value = self.tableWidget.item(row, 1).text()
        parameter = self.parameters_manager.parameters[parameter_label]
        title = "Input " + defs_pars.PARAMETER_FIELD_VALUE_TAG
        if isinstance(parameter, BooleanParameter):
            items = ['True', 'False']
            current_pos = 0
            if str_value.casefold() == ('False').casefold():
                current_pos = 1
            item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
            if ok and item:
                self.tableWidget.item(row, 1).setText(item)
        elif isinstance(parameter, DateParameter):
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dialog_button_box.accepted.connect(dialog.accept)
            dialog_button_box.rejected.connect(dialog.reject)
            layout = QVBoxLayout()
            message = QLabel("Input a date")
            layout.addWidget(message)
            str_parameter_date = str_value
            parameter_date = datetime.datetime.strptime(str_parameter_date, parameter.date_format).date()
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
                str_value = new_date.strftime(parameter.date_format)
                self.tableWidget.item(row, 1).setText(str_value)
        elif isinstance(parameter, FileParameter):
            previous_file = str_value
            path = QDir.currentPath()
            if os.path.isfile(previous_file):
                path = os.path.dirname(previous_file)
            str_files = '(*.*)'
            if parameter.domain:
                str_files = 'Files ('
                for i in range(len(parameter.domain)):
                    if i > 0:
                        str_files += ' '
                    str_files += ("*" + parameter.domain[i])
                str_files += ')'
            file_name = None
            dlg = QFileDialog()
            dlg.setWindowTitle(title)
            dlg.setDirectory(path)
            dlg.setNameFilter(str_files)
            if parameter.file_mode == defs_pars.FILE_MODE_READ:
                dlg.setFileMode(QFileDialog.ExistingFile)
                # file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            elif parameter.file_mode == defs_pars.FILE_MODE_APPEND:
                dlg.setFileMode(QFileDialog.ExistingFile)
                # file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            elif parameter.file_mode == defs_pars.FILE_MODE_WRITE:
                dlg.setFileMode(QFileDialog.AnyFile)
                # file_name, aux = QFileDialog.getSaveFileName(self, title, path, str_files)
            if dlg.exec_():
                file_names = dlg.selectedFiles()
                file_name = file_names[0]
                if file_name.casefold() != previous_file.casefold():
                    str_value = file_name
                    last_path = QFileInfo(file_name).absolutePath()
                    self.settings.setValue("last_path", last_path)
                    self.settings.sync()
                    self.tableWidget.item(row, 1).setText(str_value)
            else:
                str_value = 'None'
                self.tableWidget.item(row, 1).setText(str_value)
            # if parameter.file_mode == defs_pars.FILE_MODE_READ:
            #     file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            # elif parameter.file_mode == defs_pars.FILE_MODE_APPEND:
            #     file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
            # elif parameter.file_mode == defs_pars.FILE_MODE_WRITE:
            #     file_name, aux = QFileDialog.getSaveFileName(self, title, path, str_files)
            # # if file_name and file_name.casefold() != previous_file.casefold():
            # if file_name.casefold() != previous_file.casefold():
            #     str_value = file_name
            #     self.tableWidget.item(row, 1).setText(str_value)
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
        elif isinstance(parameter, IntegerParameter):
            current_value = int(str_value)
            domain = parameter.domain
            if len(domain) == 2:
                int_value, ok = QInputDialog.getInt(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                           current_value, domain[0], domain[1], 1)
                if ok:
                    str_value = str(eval(parameter.output_format.format(int_value)))
                    self.tableWidget.item(row, 1).setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value_aux = str(eval(parameter.output_format.format(domain[i])))
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value)
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
                if ok and item:
                    self.tableWidget.item(row, 1).setText(item)
        elif isinstance(parameter, PhysicalQuantityParameter):
            str_values = str_value.split()
            str_value = str_values[0]
            current_value = float(str_value)
            quantity_ui_unit = defs_pars.ureg.Quantity
            try:
                quantity_ui_unit = quantity_ui_unit(current_value, parameter.ui_unit)
            except Exception as quantity_error:
                str_error = (
                    'Physical Quantity Parameter: {} setting value error:\n{}'.
                    format(parameter_label, quantity_error))
                return str_error
            domain = parameter.domain
            str_unit = ''
            if parameter.output_format_unit:
                str_unit = parameter.output_format_unit.format(parameter.quantity.units)
            if len(domain) == 2:
                self.quantity_parameter = None
                self.quantity_unit_combo_box = None
                self.quantity_previous_selected_unit = None
                self.quantity_value_edit = None
                str_min_value = str(eval(parameter.output_format.format(domain[0])))
                if str_unit:
                    str_min_value += " " + str_unit
                str_max_value = str(eval(parameter.output_format.format(domain[1])))
                if parameter.output_format_unit:
                    str_max_value += " " + str_unit
                dialog = QDialog()
                dialog.setWindowTitle(title)
                dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                dialog_button_box.accepted.connect(dialog.accept)
                dialog_button_box.rejected.connect(dialog.reject)
                layout = QVBoxLayout()
                message = QLabel(("Input a value in domain: [{}, {}]:".format( str_min_value, str_max_value)))
                layout.addWidget(message)
                input_layout = QHBoxLayout()
                unit_message = QLabel("Unit:")
                self.quantity_parameter = parameter
                self.quantity_unit_combo_box = QComboBox()
                compatible_units = parameter.get_compatible_units()
                pos = -1
                str_ui_unit = str(quantity_ui_unit.units)
                for i in range(len(compatible_units)):
                    compatible_unit = compatible_units[i]
                    # str_compatible_unit = parameter.output_format_unit.format(parameter.quantity.units)
                    self.quantity_unit_combo_box.addItem(compatible_unit)
                    if compatible_unit.casefold() == str_ui_unit.casefold():
                        pos = i
                self.quantity_unit_combo_box.setCurrentIndex(pos)
                self.quantity_previous_selected_unit = self.quantity_unit_combo_box.currentText()
                self.quantity_unit_combo_box.currentIndexChanged.connect(self.select_quantity_unit)
                value_message = QLabel("Value:")
                self.quantity_value_edit = QLineEdit()
                self.quantity_value_edit.setText(str_value)
                input_layout.addWidget(unit_message)
                input_layout.addWidget(self.quantity_unit_combo_box)
                input_layout.addWidget(value_message)
                input_layout.addWidget(self.quantity_value_edit)
                layout.addLayout(input_layout)
                layout.addWidget(dialog_button_box)
                dialog.setLayout(layout)
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    new_str_value = self.quantity_value_edit.text()
                    new_unit = self.quantity_unit_combo_box.currentText()
                    if new_str_value == str_value and new_unit == str_unit:
                        self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                        self.quantity_parameter = None
                        self.quantity_unit_combo_box = None
                        self.quantity_previous_selected_unit = None
                        self.quantity_value_edit = None
                        return
                    real_value = None
                    try:
                        real_value = float(new_str_value)
                    except ValueError:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                        self.quantity_parameter = None
                        self.quantity_unit_combo_box = None
                        self.quantity_previous_selected_unit = None
                        self.quantity_value_edit = None
                        return
                    quantity_selected_unit = defs_pars.ureg.Quantity
                    try:
                        quantity_selected_unit = quantity_selected_unit(real_value, new_unit)
                    except Exception as quantity_error:
                        str_error = (
                            'Physical Quantity Parameter: {} setting value error:\n{}'.
                            format(parameter_label, quantity_error))
                        self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                        self.quantity_parameter = None
                        self.quantity_unit_combo_box = None
                        self.quantity_previous_selected_unit = None
                        self.quantity_value_edit = None
                        return str_error
                    new_quantity_ui_unit = quantity_selected_unit.to(parameter.ui_unit)
                    new_ui_value = new_quantity_ui_unit.magnitude
                    if new_ui_value < domain[0] or new_ui_value > domain[1]:
                        msg = ('Value must be a real number in domain: [{}, {}]'
                               .format(str_min_value, str_max_value))
                        QMessageBox.information(self, 'Information', msg)
                        self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                        self.quantity_parameter = None
                        self.quantity_unit_combo_box = None
                        self.quantity_previous_selected_unit = None
                        self.quantity_value_edit = None
                        return
                    str_value = str(eval(parameter.output_format.format(new_ui_value)))
                    if str_unit:
                        str_value += " " + str_unit
                    self.tableWidget.item(row, 1).setText(str_value)
                    self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                    self.quantity_parameter = None
                    self.quantity_unit_combo_box = None
                    self.quantity_previous_selected_unit = None
                    self.quantity_value_edit = None
                else:
                    self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                    self.quantity_parameter = None
                    self.quantity_unit_combo_box = None
                    self.quantity_previous_selected_unit = None
                    self.quantity_value_edit = None
                # text, ok = QInputDialog.getText(self, title, msg,
                #                                 QLineEdit.Normal, str_value)
                # if ok:
                #     real_value = None
                #     try:
                #         real_value = float(text)
                #     except ValueError:
                #         msg = ('Value must be a real number in domain: [{}, {}]'
                #                .format(str_min_value, str_max_value))
                #         QMessageBox.information(self, 'Information', msg)
                #         return
                #     if real_value < domain[0] or real_value > domain[1]:
                #         msg = ('Value must be a real number in domain: [{}, {}]'
                #                .format(str_min_value, str_max_value))
                #         QMessageBox.information(self, 'Information', msg)
                #         return
                #     str_value = str(eval(parameter.output_format.format(real_value)))
                #     if str_unit:
                #         str_value += " " + str_unit
                #     self.tableWidget.item(row, 1).setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value_aux = str(eval(parameter.output_format.format(domain[i])))
                    if str_unit:
                        str_value_aux += " " + str_unit
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value.text())
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items,
                                                current_pos, False)
                if ok and item:
                    self.tableWidget.item(row, 1).setText(item)
        elif isinstance(parameter, RealParameter):
            current_value = float(str_value)
            domain = parameter.domain
            if len(domain) == 2:
                str_min_value = str(eval(parameter.output_format.format(domain[0])))
                str_max_value = str(eval(parameter.output_format.format(domain[1])))
                msg = ("Input a value in domain: [{}, {}]:".format(str_min_value, str_max_value))
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
                    str_value = str(eval(parameter.output_format.format(real_value)))
                    self.tableWidget.item(row, 1).setText(str_value)
            else:
                items = []
                for i in range(len(domain)):
                    str_value_aux = str(eval(parameter.output_format.format(domain[i])))
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value)
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items,
                                                current_pos, False)
                if ok and item:
                    self.tableWidget.item(row, 1).setText(item)
        elif isinstance(parameter, StringParameter):
            if not parameter.domain:
                text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                QLineEdit.Normal, str_value)
                # if ok and text != '' and text != str_value:
                if ok and text != str_value:
                    self.tableWidget.item(row, 1).setText(text)
            else:
                items = []
                for i in range(len(parameter.domain)):
                    str_value_aux = parameter.domain[i]
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value)
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
                if ok and item:
                    self.tableWidget.item(row, 1).setText(item)
        elif isinstance(parameter, VectorLayerFieldNameParameter):
            domain = parameter.domain
            mandatory = parameter.mandatory
            dialog = VectorLayerFieldDialog(title, parameter_label, str_value, domain, mandatory,
                                            self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return
            dialog_result = dialog.exec()
            if dialog_result == QDialog.Accepted:
                str_error, new_str_value = dialog.get_value_as_string()
                if str_error:
                    QMessageBox.information(self, 'Information', str_error)
                    dialog.exec()
                if new_str_value != str_value:
                    self.tableWidget.item(row, 1).setText(new_str_value)
        else:
            text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                            QLineEdit.Normal, str_value)
            # if ok and text != '' and text != str_value:
            if ok and text != str_value:
                self.tableWidget.item(row, 1).setText(text)
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


