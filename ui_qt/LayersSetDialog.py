# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math
import json
import copy

current_path = os.path.dirname(os.path.realpath(__file__))
# current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))
sys.path.append(os.path.join(current_path, '../..'))
# sys.path.insert(0, '..')
# sys.path.insert(0, '../..')

from qgis.PyQt import QtCore, QtWidgets
from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog, QHBoxLayout, QDoubleSpinBox,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit, QDateEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView)
from qgis.PyQt.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate
from qgis.PyQt.QtGui import QStandardItemModel

import defs_pars
from Parameter import *
from ParametersManager import ParametersManager
from .ParameterDialog import ParameterDialog

from pyLibCRSs import CRSsDefines as defs_crs
from pyLibCRSs.CRSsTools import CRSsTools
from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
from ui_qt.VectorLayerFieldDialog import VectorLayerFieldDialog
from ui_qt.VectorLayerDialog import VectorLayerDialog
from ui_qt.RasterLayerDialog import RasterLayerDialog
from ui_qt.LayerSetDialog import LayerSetDialog
from pyLibQtTools.Tools import SimpleTextEditDialog
from pyLibQtTools.JsonModel import JsonModel
from pyLibQtTools.Tools import SimpleTextEditDialog
from pyLibQtTools.CheckableComboBox import CheckableComboBox
# from pyLibQGIS.QGISTools import QGISTools

class LayersSetDialog(QDialog):

    def __init__(self,
                 title,
                 label,
                 parameter,
                 domain,
                 mandatory,
                 qgis_iface,
                 settings,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'LayersSetDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.file_path_selected = None #input
        self.parameter = parameter
        # self.layer_names_selected = []
        self.file_path_selected = None
        self.layer_names = []
        self.layer_names_selected = []
        self.parameter_by_row_by_column = {}
        self.layer_name_column = -1
        self.layer_type_column = -1
        self.layer_style_column = -1
        self.use_layer_style_column = -1
        self.parameters_by_layer_name_selected = {}
        # self.layer_geometry_ogr_wkb_type = []
        self.layer_type_by_name = {}
        self.parameter_def_by_column = {}
        self.layer_styles_by_layer_name = {}
        self.layer_style_used_as_default_by_layer_name = {}
        self.str_error = self.initialize()
        self.accepted = False

    def on_accept(self):
        if self.save():
            self.accepted = True
            self.accept()
        return

    def add_file(self):
        last_path = self.settings.value("last_path")
        if not last_path:
            previous_file_path = self.fileComboBox.currentText()
            if previous_file_path != defs_pars.NO_COMBO_SELECT:
                last_path = QFileInfo(previous_file_path).absolutePath()
            else:
                last_path = QDir.currentPath()
            self.settings.setValue("last_path", last_path)
            self.settings.sync()
        title = "Select Layer Set File"
        dlg = QFileDialog()
        dlg.setDirectory(last_path)
        # dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setNameFilter("Layer Set File (*.gpkg)")
        if dlg.exec_():
            file_names = dlg.selectedFiles()
            file_name = file_names[0]
        else:
            return
        if file_name:
            str_error, is_vector = GDALTools.is_vector(file_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                return
            last_path = QFileInfo(file_name).absolutePath()
            self.settings.setValue("last_path", last_path)
            self.settings.sync()
            self.fileComboBox.addItem(file_name)
            self.fileComboBox.setCurrentText(file_name)
        return

    def file_changed(self):
        file_path = self.fileComboBox.currentText()
        self.layer_names.clear()
        self.parameter_by_row_by_column = {}
        self.layer_name_column = -1
        self.layer_type_column = -1
        self.layer_style_column = -1
        self.use_layer_style_column = -1
        self.tableWidget.setRowCount(0)
        self.layer_styles_by_layer_name = {}
        self.layer_style_used_as_default_by_layer_name = {}
        if file_path == defs_pars.NO_COMBO_SELECT:
            return
        str_error, driver_name = GDALTools.get_driver_name_from_file(file_path)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        str_error, layer_names = GDALTools.get_layers_names(file_path)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        str_error, raster_layer_names = GDALTools.get_raster_layers_names(file_path)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        if len(layer_names) == 0:
            str_error = ('There are no layers in:\n{}'.format(file_path))
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        for i in range(len(layer_names)):
            layer_name = layer_names[i]
            str_error, geometry_type = GDALTools.get_layer_geometry_type(file_path, layer_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                return
            if geometry_type == defs_gdal.geometry_type_by_name['none']:
                continue
            self.layer_type_by_name[layer_name] = defs_gdal.GDAL_ALIAS_VECTOR
            self.layer_names.append(layer_name)
        for i in range(len(raster_layer_names)):
            layer_name = raster_layer_names[i]
            self.layer_type_by_name[layer_name] = defs_gdal.GDAL_ALIAS_RASTER
            self.layer_names.append(layer_name)
        str_error, exists_styles = GDALTools.exists_layer(file_path, defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES)
        if str_error:
            str_error = ('Getting if exists styles from file:\n{}\nError:\n{}'.format(file_path, str_error))
            QMessageBox.information(self, 'Information', str_error)
            return
        if exists_styles:
            fields = {}
            field_name = defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_LAYER_NAME
            fields[field_name] = defs_gdal.type_by_name['string']
            field_name = defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_LAYER_STYLE_NAME
            fields[field_name] = defs_gdal.type_by_name['string']
            field_name = defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_USE_AS_DEFAULT
            fields[field_name] = defs_gdal.type_by_name['string']
            # field_geometry = defs_project.LOCATIONS_FIELD_GEOMETRY
            # fields[field_geometry] = defs_project.fields_by_layer[defs_project.LOCATIONS_LAYER_NAME][field_geometry]
            filter_fields = None
            str_error, features = GDALTools.get_features(file_path,
                                                         defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES,
                                                         fields,
                                                         filter_fields,
                                                         wfs = None)
            if str_error:
                str_error = ('Getting styles from file:\n{}\nError:\n{}'.format(file_path, str_error))
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
                return
            for i in range(len(features)):
                layer_name = features[i][defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_LAYER_NAME]
                layer_style = features[i][defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_LAYER_STYLE_NAME]
                use_as_default = features[i][defs_gdal.GEOPACKAGE_TABLE_LAYER_STYLES_FIELD_USE_AS_DEFAULT]
                if not layer_name in self.layer_styles_by_layer_name:
                    self.layer_styles_by_layer_name[layer_name] = []
                    # self.layer_styles_by_layer_name[layer_name].append('')
                    self.layer_style_used_as_default_by_layer_name[layer_name] = ''
                self.layer_styles_by_layer_name[layer_name].append(layer_style)
                if use_as_default == '1':
                    self.layer_style_used_as_default_by_layer_name[layer_name] = layer_style
        need_to_save = False
        for layer_name in self.layer_names:
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.parameter_by_row_by_column[rowPosition] = {}
            used_layer = False
            if self.file_path_selected and os.path.normpath(self.file_path_selected) == os.path.normpath(file_path):
                for j in range(len(self.layer_names_selected)):
                    layer_name_selected = self.layer_names_selected[j]
                    if layer_name_selected.casefold() == layer_name.casefold():
                        used_layer = True
                        break
            for col in self.parameter_def_by_column:
                parameter_label = self.parameter_def_by_column[col][defs_pars.PARAMETER_FIELD_LABEL]
                if parameter_label.casefold() == defs_pars.TAG_LAYER_NAME_VALUE.casefold():
                    item = QTableWidgetItem(layer_name)
                    item.setTextAlignment(Qt.AlignCenter)
                    if not used_layer:
                        item.setCheckState(QtCore.Qt.Unchecked)
                    else:
                        item.setCheckState(QtCore.Qt.Checked)
                    currentState = item.checkState()
                    item.setData(QtCore.Qt.UserRole, currentState)
                    self.tableWidget.setItem(rowPosition, col, item)
                    if self.layer_name_column == -1:
                        self.layer_name_column = col
                    break
            for col in self.parameter_def_by_column:
                parameter_label = self.parameter_def_by_column[col][defs_pars.PARAMETER_FIELD_LABEL]
                parameter_to_use = None
                if not used_layer:
                    parameter_to_use = self.parameter.parameters_manager.parameters[parameter_label]
                else:
                    parameter_to_use = self.parameters_by_layer_name_selected[layer_name][parameter_label]
                self.parameter_by_row_by_column[rowPosition][col] = parameter_to_use
                if parameter_label.casefold() == defs_pars.TAG_LAYER_NAME_VALUE.casefold():
                    continue
                str_value = str(parameter_to_use)
                if parameter_label.casefold() == defs_pars.TAG_LAYER_TYPE_VALUE.casefold():
                    str_value = self.layer_type_by_name[layer_name]
                    if self.layer_type_column == -1:
                        self.layer_type_column = col
                if parameter_label.casefold() == defs_pars.TAG_LAYER_STYLE_VALUE.casefold():
                    if self.layer_style_column == -1:
                        self.layer_style_column = col
                if parameter_label.casefold() == defs_pars.TAG_USE_LAYER_STYLE_VALUE.casefold():
                    if not used_layer:
                        str_value = 'False'
                    if self.use_layer_style_column == -1:
                        self.use_layer_style_column = col
                item = QTableWidgetItem(str_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(rowPosition, col, item)
            for col in self.parameter_def_by_column:
                if col == self.layer_name_column:
                    continue
                item = self.tableWidget.item(rowPosition, col)
                item_flags = item.flags()
                if used_layer and col != self.layer_type_column:# and col != self.layer_style_column:
                    item_flags |= QtCore.Qt.ItemIsEnabled
                else:
                    item_flags &= ~QtCore.Qt.ItemIsEnabled
                if not exists_styles and col == self.use_layer_style_column:
                    item_flags &= ~QtCore.Qt.ItemIsEnabled
                item.setFlags(item_flags)
            if not used_layer:
                self.tableWidget.item(rowPosition, self.use_layer_style_column).setText('False')
                self.tableWidget.item(rowPosition, self.layer_style_column).setText('')
                continue
            str_item_use_layer_style = self.tableWidget.item(rowPosition, self.use_layer_style_column).text()
            use_layer_style = False
            if str_item_use_layer_style.casefold() == 'True'.casefold():
                use_layer_style = True
            str_item_layer_style = self.tableWidget.item(rowPosition, self.layer_style_column).text()
            if not use_layer_style:
                if str_item_layer_style:
                    self.tableWidget.item(rowPosition, self.layer_style_column).setText('')
                    if not need_to_save:
                        need_to_save = True
            else:
                if not layer_name in self.layer_styles_by_layer_name:
                    self.tableWidget.item(rowPosition, self.layer_style_column).setText('')
                    self.tableWidget.item(rowPosition, self.use_layer_style_column).setText('False')
                    if not need_to_save:
                        need_to_save = True
                else:
                    # if self.layer_style_used_as_default_by_layer_name[layer_name]:
                    layer_style = self.layer_style_used_as_default_by_layer_name[layer_name]# '' or style name
                    if layer_style.casefold() != str_item_layer_style.casefold():
                        self.tableWidget.item(rowPosition, self.layer_style_column).setText(layer_style)
                        if not need_to_save:
                            need_to_save = True
        if need_to_save:
            self.save()
            self.file_changed()
        return
    #
    # def get_value_as_string(self):
    #     str_error = ''
    #     str_value = ''
    #     file_path = ''
    #     layers = None
    #     file_path = self.fileComboBox.currentText()
    #     if file_path == defs_pars.NO_COMBO_SELECT:
    #         if self.mandatory:
    #             str_error = ('No file selected')
    #             return str_error, self.value_as_string
    #         else:
    #             file_path = ''
    #     else:
    #         layers = self.layerComboBox.get_checked_texts()
    #     self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
    #     self.value_as_dict[defs_pars.TAG_LAYERS] = layers
    #     self.value_as_string = json.dumps(self.value_as_dict)
    #     return str_error, self.value_as_string

    def initialize(self):
        str_error = ''
        parameters_as_list_of_dict = self.parameter.parameters_manager.parameters_as_list_of_dict
        self.tableWidget.setColumnCount(len(parameters_as_list_of_dict))
        self.tableWidget.setStyleSheet("QHeaderView::section { color:black; background : lightGray; }")
        for i in range(len(parameters_as_list_of_dict)):
            parameter = parameters_as_list_of_dict[i]
            header_item = QTableWidgetItem(parameter[defs_pars.PARAMETER_FIELD_LABEL])
            header_tooltip = parameter[defs_pars.PARAMETER_FIELD_DESCRIPTION]
            header_item.setToolTip(header_tooltip)
            self.tableWidget.setHorizontalHeaderItem(i, header_item)
            self.parameter_def_by_column[i] = parameter
        self.tableWidget.setSortingEnabled(True)
        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        value = self.parameter.value
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Layers Set Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYERS in value:
            str_error = ('Layers Set Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYERS))
            return str_error
        file_name = value[defs_pars.TAG_FILE_PATH]
        if file_name:
            if not os.path.exists(file_name):
                msg = ('Not exists file:\n{}'.format(file_name))
                QMessageBox.information(self, 'Information', msg)
                file_name = ''
            self.file_path = file_name
            self.file_path_selected = file_name
            if self.file_path:
                self.fileComboBox.addItem(self.file_path)
            for i in range(len(self.parameter.layers_parameters_manager)):
                layer_parameter_manager = self.parameter.layers_parameters_manager[i]
                layer_parameters = layer_parameter_manager.parameters
                layer_name = str(layer_parameters[defs_pars.TAG_LAYER_NAME_VALUE])
                self.layer_names_selected.append(layer_name)
                self.parameters_by_layer_name_selected[layer_name] = layer_parameters
        self.fileComboBox.setEnabled(True)
        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)
            # self.file_changed()
        self.tableWidget.itemDoubleClicked.connect(self.on_click)
        self.tableWidget.itemClicked.connect(self.on_click)
        self.addFilePushButton.clicked.connect(self.add_file)
        self.acceptPushButton.clicked.connect(self.on_accept)
        return str_error

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def on_click(self, item):
        row = item.row()
        col = item.column()
        str_value = item.text()
        parameter_label = self.tableWidget.horizontalHeaderItem(col).text()
        if parameter_label.casefold() == defs_pars.TAG_LAYER_NAME_VALUE.casefold():
            currentState = item.checkState()
            for col in self.parameter_def_by_column:
                if col == self.layer_name_column:
                    continue
                item = self.tableWidget.item(row, col)
                item_flags = item.flags()
                if (currentState == Qt.CheckState.Checked
                        and col != self.layer_type_column): # and col != self.layer_style_column):
                    item_flags |= QtCore.Qt.ItemIsEnabled
                else:
                    item_flags &= ~QtCore.Qt.ItemIsEnabled
                if not bool(self.layer_styles_by_layer_name) and col == self.use_layer_style_column:
                    item_flags &= ~QtCore.Qt.ItemIsEnabled
                item.setFlags(item_flags)
            return
        item_layer_name = self.tableWidget.item(row, self.layer_name_column)
        if item_layer_name.checkState() == Qt.CheckState.Unchecked:
            return
        str_error = self.set_value(row, col)
        if str_error:
            str_error = ('Setting parameter: {}, error:\n{}'.
                         format(parameter_label, str_error))
            QMessageBox.information(self, 'Information', str_value, str_error)
        if col == self.use_layer_style_column:
            layer_name = item_layer_name.text()
            if layer_name in self.layer_styles_by_layer_name:
                item_layer_style = self.tableWidget.item(row, self.layer_style_column)
                str_item_use_layer_style = self.tableWidget.item(row, col).text()
                if str_item_use_layer_style.casefold() == 'true'.casefold():
                    layer_style = self.layer_style_used_as_default_by_layer_name[layer_name]
                    item_layer_style.setText(layer_style)
                else:
                    item.setText('False')
                    item_layer_style.setText('')
        return

    def save(self):
        parameter_value = {}
        file_path = self.fileComboBox.currentText()
        original_parameters_manager = copy.deepcopy(self.parameter.parameters_manager)
        layers = []
        layers_parameters_manager = []
        if file_path == defs_pars.NO_COMBO_SELECT:
            file_path = None
        for row in range(self.tableWidget.rowCount()):
            item_layer_name = self.tableWidget.item(row, self.layer_name_column)
            if item_layer_name.checkState() == Qt.CheckState.Unchecked:
                continue
            layer_name = item_layer_name.text()
            layer = []
            parameters_dictionary_list = []
            for col in self.parameter_def_by_column:
                parameter_label = self.parameter_def_by_column[col][defs_pars.PARAMETER_FIELD_LABEL]
                # parameter = self.parameters_by_layer_name_selected[layer_name][parameter_label]
                parameter = self.parameter_by_row_by_column[row][col]
                str_value = self.tableWidget.item(row, col).text()
                parameter_as_dict = {}
                for aux_parameter_as_dict in self.parameter.parameters_manager.parameters_as_list_of_dict:
                    if parameter.label.casefold() == aux_parameter_as_dict[defs_pars.PARAMETER_FIELD_LABEL].casefold():
                        parameter_as_dict = copy.deepcopy(aux_parameter_as_dict)
                        break
                parameter.set_value(str_value)
                if isinstance(parameter, DateParameter):
                    parameter_as_dict[defs_pars.PARAMETER_FIELD_VALUE] = str(parameter)
                else:
                    parameter_as_dict[defs_pars.PARAMETER_FIELD_VALUE] = parameter.value
                parameter_as_string = json.dumps(parameter_as_dict)
                # layer.append(parameter_as_string)
                layer.append(parameter_as_dict)
                parameters_dictionary_list.append(parameter_as_dict)
            layers.append(layer)
            layer_parameters_manager = ParametersManager()
            str_error = layer_parameters_manager.initialize(parameters_dictionary_list)
            if str_error:
                msg = ('Saving layer: {}, error:\n{}'.format(layer_name, str_error))
                QMessageBox.information(self, 'Information', msg)
                self.parameter.parameters_manager = original_parameters_manager
                return False
            layers_parameters_manager.append(layer_parameters_manager)
        parameter_value[defs_pars.TAG_FILE_PATH] = file_path
        parameter_value[defs_pars.TAG_LAYERS] = layers
        self.parameter.value = parameter_value
        self.parameter.layers_parameters_manager = layers_parameters_manager
        self.parameter.parameters_manager = original_parameters_manager
        return True

    def set_value(self, row, col):
        str_error = ''
        parameter_label = self.tableWidget.horizontalHeaderItem(col).text()
        str_value = self.tableWidget.item(row, col).text()
        parameter = self.parameter_by_row_by_column[row][col]
        mandatory = parameter.mandatory
        title = "Input " + defs_pars.PARAMETER_FIELD_VALUE_TAG
        if col == self.layer_style_column:
            layer_name = self.tableWidget.item(row, self.layer_name_column).text()
            if not layer_name in self.layer_styles_by_layer_name:
                return
            items = self.layer_styles_by_layer_name[layer_name]
            current_pos = items.index(str_value)
            item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
            if ok:# and item:
                self.tableWidget.item(row, col).setText(item)
            return
        if isinstance(parameter, BooleanParameter):
            items = ['True', 'False']
            current_pos = 0
            if str_value.casefold() == ('False').casefold():
                current_pos = 1
            item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items, current_pos, False)
            if ok and item:
                self.tableWidget.item(row, col).setText(item)
        elif isinstance(parameter, DateParameter):
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dialog_button_box.accepted.connect(dialog.accept)
            dialog_button_box.rejected.connect(dialog.reject)
            layout = QVBoxLayout()
            message = QLabel("Input a date")
            layout.addWidget(message)
            parameter_date = datetime.date.today()
            if str_value and str_value != 'None':
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
                if not str_value and mandatory:
                    msg = ('Parameter: {} is mandatory'.format(parameter_label))
                    QMessageBox.information(self, 'Information', msg)
                    self.set_value(row, col)
                self.tableWidget.item(row, col).setText(str_value)
        elif isinstance(parameter, FileParameter):
            previous_file = str_value
            path = None
            if os.path.isfile(previous_file):
                path = os.path.dirname(previous_file)
            else:
                path = self.settings.value("last_path")
                if not path:
                    path = QDir.currentPath()
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
                    if not str_value and mandatory:
                        msg = ('Parameter: {} is mandatory'.format(parameter_label))
                        QMessageBox.information(self, 'Information', msg)
                        self.set_value(row, col)
                    last_path = QFileInfo(file_name).absolutePath()
                    self.settings.setValue("last_path", last_path)
                    self.settings.sync()
                    self.tableWidget.item(row, col).setText(str_value)
            else:
                if not str_value and mandatory:
                    msg = ('Parameter: {} is mandatory'.format(parameter_label))
                    QMessageBox.information(self, 'Information', msg)
                    self.set_value(row, col)
                # str_value = 'None'
                # self.tableWidget.item(row, 1).setText(str_value)
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
            domain = parameter.domain
            current_value = 0
            if len(domain) == 2:
                current_value = domain[0]
            try:
                current_value = int(str_value)
            except ValueError as verr:
                pass  # do job to handle: s does not contain anything convertible to int
            except Exception as ex:
                pass
            if len(domain) == 2:
                int_value, ok = QInputDialog.getInt(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                           current_value, domain[0], domain[1], 1)
                if ok:
                    str_value = str(eval(parameter.output_format.format(int_value)))
                    if not str_value and mandatory:
                        msg = ('Parameter: {} is mandatory'.format(parameter_label))
                        QMessageBox.information(self, 'Information', msg)
                        self.set_value(row, col)
                    self.tableWidget.item(row, col).setText(str_value)
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
                    self.tableWidget.item(row, col).setText(item)
        elif isinstance(parameter, LayersSetParameter):
            domain = parameter.domain
            dialog = LayersSetDialog(title, parameter_label, parameter, domain, mandatory,
                                     self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return str_error
            new_str_value = str_value
            while True:
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    str_error, new_str_value = dialog.get_value_as_string()
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                    else:
                        break
                else:
                    break
            if new_str_value != str_value:
                self.tableWidget.item(row, col).setText(new_str_value)
        elif isinstance(parameter, LayerSetParameter):
            domain = parameter.domain
            dialog = LayerSetDialog(title, parameter_label, str_value, domain, mandatory,
                                    self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return str_error
            new_str_value = str_value
            while True:
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    str_error, new_str_value = dialog.get_value_as_string()
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                    else:
                        break
                else:
                    break
            if new_str_value != str_value:
                self.tableWidget.item(row, col).setText(new_str_value)
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
            str_ui_unit_acronym = ''
            if parameter.output_format_unit:
                str_unit = parameter.output_format_unit.format(parameter.quantity.units)
                str_ui_unit_acronym = parameter.output_format_unit.format(quantity_ui_unit.units)
            if len(domain) == 2:
                self.quantity_parameter = None
                self.quantity_unit_combo_box = None
                self.quantity_previous_selected_unit = None
                self.quantity_value_edit = None
                str_min_value = str(eval(parameter.output_format.format(domain[0])))
                if str_ui_unit_acronym:
                    str_min_value += " " + str_ui_unit_acronym
                str_max_value = str(eval(parameter.output_format.format(domain[1])))
                if parameter.output_format_unit:
                    str_max_value += " " + str_ui_unit_acronym
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
                    if compatible_unit.casefold() == str_ui_unit.casefold():
                        pos = i
                        self.quantity_unit_combo_box.addItem(str_ui_unit)
                    else:
                        self.quantity_unit_combo_box.addItem(compatible_unit)
                # # str_compatible_unit = parameter.output_format_unit.format(parameter.quantity.units)
                    # self.quantity_unit_combo_box.addItem(compatible_unit)
                    # if compatible_unit.casefold() == str_ui_unit.casefold():
                    #     pos = i
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
                    if new_str_value == str_value and new_unit == str_ui_unit:
                        self.quantity_unit_combo_box.currentIndexChanged.disconnect()
                        self.quantity_parameter = None
                        self.quantity_unit_combo_box = None
                        self.quantity_previous_selected_unit = None
                        self.quantity_value_edit = None
                        return str_error
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
                        return str_error
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
                        return str_error
                    str_value = str(eval(parameter.output_format.format(new_ui_value)))
                    # if str_ui_unit:
                    #     str_value += " " + str_ui_unit
                    if str_ui_unit_acronym:
                        str_value += " " + str_ui_unit_acronym
                    if not str_value and mandatory:
                        msg = ('Parameter: {} is mandatory'.format(parameter_label))
                        QMessageBox.information(self, 'Information', msg)
                        self.set_value(row, col)
                    self.tableWidget.item(row, col).setText(str_value)
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
                        str_value_aux += " " + str_ui_unit_acronym
                        # str_value_aux += " " + str_unit
                    items.append(str_value_aux)
                current_pos = 0
                if str_value in items:
                    current_pos = items.index(str_value.text())
                item, ok = QInputDialog.getItem(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG, items,
                                                current_pos, False)
                if ok and item:
                    self.tableWidget.item(row, col).setText(item)
        elif isinstance(parameter, RealParameter):
            domain = parameter.domain
            current_value = 0
            if len(domain) == 2:
                str_min_value = str(eval(parameter.output_format.format(domain[0])))
                try:
                    current_value = float(str_min_value)
                except ValueError as verr:
                    pass  # do job to handle: s does not contain anything convertible to int
                except Exception as ex:
                    pass
            try:
                current_value = float(str_value)
            except ValueError as verr:
                pass  # do job to handle: s does not contain anything convertible to int
            except Exception as ex:
                pass
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
                    if not str_value and mandatory:
                        msg = ('Parameter: {} is mandatory'.format(parameter_label))
                        QMessageBox.information(self, 'Information', msg)
                        self.set_value(row, col)
                    self.tableWidget.item(row, col).setText(str_value)
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
                    self.tableWidget.item(row, col).setText(item)
        elif isinstance(parameter, StringParameter):
            if not parameter.domain:
                text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                                QLineEdit.Normal, str_value)
                # if ok and text != '' and text != str_value:
                if ok and text != str_value:
                    str_value = text
                    # if not str_value and mandatory:
                    #     msg = ('Parameter: {} is mandatory'.format(parameter_label))
                    #     QMessageBox.information(self, 'Information', msg)
                    #     self.set_value(row, col)
                    self.tableWidget.item(row, col).setText(str_value)
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
                    self.tableWidget.item(row, col).setText(item)
        elif isinstance(parameter, RasterLayerParameter):
            domain = parameter.domain
            dialog = RasterLayerDialog(title, parameter_label, str_value, domain, mandatory,
                                       self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return
            new_str_value = str_value
            while True:
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    str_error, new_str_value = dialog.get_value_as_string()
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                    else:
                        break
                else:
                    break
            if new_str_value != str_value:
                self.tableWidget.item(row, col).setText(new_str_value)
        elif isinstance(parameter, VectorLayerParameter):
            domain = parameter.domain
            dialog = VectorLayerDialog(title, parameter_label, str_value, domain, mandatory,
                                       self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return str_error
            new_str_value = str_value
            while True:
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    str_error, new_str_value = dialog.get_value_as_string()
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                    else:
                        break
                else:
                    break
            if new_str_value != str_value:
                self.tableWidget.item(row, col).setText(new_str_value)
        elif isinstance(parameter, VectorLayerFieldNameParameter):
            domain = parameter.domain
            dialog = VectorLayerFieldDialog(title, parameter_label, str_value, domain, mandatory,
                                            self.qgis_iface, self.settings,  self)
            if dialog.str_error:
                QMessageBox.information(self, 'Information', dialog.str_error)
                return str_error
            new_str_value = str_value
            while True:
                dialog_result = dialog.exec()
                if dialog_result == QDialog.Accepted:
                    str_error, new_str_value = dialog.get_value_as_string()
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                    else:
                        break
                else:
                    break
            if new_str_value != str_value:
                self.tableWidget.item(row, col).setText(new_str_value)
        else:
            text, ok = QInputDialog.getText(self, title, defs_pars.PARAMETER_FIELD_VALUE_TAG,
                                            QLineEdit.Normal, str_value)
            # if ok and text != '' and text != str_value:
            if ok and text != str_value:
                str_value = text
                if not str_value and mandatory:
                    msg = ('Parameter: {} is mandatory'.format(parameter_label))
                    QMessageBox.information(self, 'Information', msg)
                    self.set_value(row, col)
                self.tableWidget.item(row, col).setText(str_value)
        return str_error
