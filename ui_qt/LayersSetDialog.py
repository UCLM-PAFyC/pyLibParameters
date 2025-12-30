# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math
import json

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog, QHBoxLayout, QDoubleSpinBox,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit, QDateEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate
from PyQt5.QtGui import QStandardItemModel

import defs_pars
from Parameter import *
from .ParameterDialog import ParameterDialog

from pyLibCRSs import CRSsDefines as defs_crs
from pyLibCRSs.CRSsTools import CRSsTools
from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
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
        self.parameters_by_layer_name_selected = {}
        # self.layer_geometry_ogr_wkb_type = []
        self.layer_type_by_name = {}
        self.parameter_def_by_column = {}
        self.str_error = self.initialize()

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
        self.tableWidget.setRowCount(0)
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
            self.layer_type_by_name[layer_name] = defs_gdal.GDAL_ALIAS_VECTOR
            self.layer_names.append(layer_name)
        for i in range(len(raster_layer_names)):
            layer_name = raster_layer_names[i]
            self.layer_type_by_name[layer_name] = defs_gdal.GDAL_ALIAS_RASTER
            self.layer_names.append(layer_name)
        for layer_name in self.layer_names:
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            used_layer = False
            if os.path.normpath(self.file_path_selected) == os.path.normpath(file_path):
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
                    break
            for col in self.parameter_def_by_column:
                parameter_label = self.parameter_def_by_column[col][defs_pars.PARAMETER_FIELD_LABEL]
                if parameter_label.casefold() == defs_pars.TAG_LAYER_NAME_VALUE.casefold():
                    continue
                parameter_to_use = None
                if not used_layer:
                    parameter_to_use = self.parameter.parameters_manager.parameters[parameter_label]
                else:
                    parameter_to_use = self.parameters_by_layer_name_selected[layer_name][parameter_label]
                str_value = str(parameter_to_use)
                item = QTableWidgetItem(str_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(rowPosition, col, item)
        return

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
        self.addFilePushButton.clicked.connect(self.add_file)
        return str_error
