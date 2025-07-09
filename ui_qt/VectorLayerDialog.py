# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys
import math
import json

current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '..'))

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (QApplication, QMessageBox, QDialog, QInputDialog, QHBoxLayout, QDoubleSpinBox,
                             QFileDialog, QPushButton, QComboBox, QPlainTextEdit, QLineEdit, QDateEdit,
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate

import defs_pars
from Parameter import *
from .ParameterDialog import ParameterDialog

from pyLibCRSs import CRSsDefines as defs_crs
from pyLibCRSs.CRSsTools import CRSsTools
from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
from pyLibQGIS.QGISTools import QGISTools


from .Tools import SimpleTextEditDialog


class VectorLayerDialog(QDialog):
    """Employee dialog."""

    def __init__(self,
                 title,
                 label,
                 str_value,
                 domain,
                 mandatory,
                 qgis_iface,
                 settings,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'VectorLayerDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_name = None
        self.layer_geometry_ogr_wkb_type = []
        self.qgis_layers_by_name = {}
        self.str_error = self.initialize(str_value)

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
        title = "Select Vector File"
        dlg = QFileDialog()
        dlg.setDirectory(last_path)
        # dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setNameFilter("Vector File (*.*)")
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
        self.layerComboBox.clear()
        self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.layerComboBox.setEnabled(False)
        self.newLayerPushButton.setEnabled(False)
        if file_path == defs_pars.NO_COMBO_SELECT:
            return
        current_position = 0
        if file_path == defs_qgis.QGIS_PROJECT_TAG:
            for qgis_layer_name in self.qgis_layers_by_name:
                self.layerComboBox.addItem(qgis_layer_name)
                if qgis_layer_name.casefold() == self.layer_name.casefold():
                    current_position = self.layerComboBox.findText(qgis_layer_name)
        else:
            str_error, driver_name = GDALTools.get_driver_name_from_file(file_path)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
            str_error, layer_names = GDALTools.get_layers_names(file_path)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
            if len(layer_names) == 0:
                str_error = ('There are no layers in:\n{}'.format(file_path))
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
            for i in range(len(layer_names)):
                layer_name = layer_names[i]
                if self.layer_name:
                    str_error, geometry_type = GDALTools.get_layer_geometry_type(file_path, layer_name)
                    if str_error:
                        QMessageBox.information(self, 'Information', str_error)
                        return
                    if geometry_type in self.layer_geometry_ogr_wkb_type:
                        if layer_name.casefold() == self.layer_name.casefold():
                            current_position = i + 1
                        self.layerComboBox.addItem(layer_name)
        self.layerComboBox.setEnabled(True)
        self.layerComboBox.setCurrentIndex(current_position)
        return

    def get_value_as_string(self):
        str_error = ''
        str_value = ''
        file_path = ''
        layer_name = ''
        file_path = self.fileComboBox.currentText()
        if file_path == defs_pars.NO_COMBO_SELECT:
            if self.mandatory:
                str_error = ('No file selected')
                return str_error, self.value_as_string
            else:
                file_path = ''
        else:
            layer_name = self.layerComboBox.currentText()
            if layer_name == defs_pars.NO_COMBO_SELECT:
                if self.mandatory:
                    str_error = ('No layer selected')
                    return str_error, self.value_as_string
                else:
                    file_path = ''
                    layer_name = ''
        self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
        self.value_as_dict[defs_pars.TAG_LAYER_NAME] = layer_name
        self.value_as_string = json.dumps(self.value_as_dict)
        return str_error, self.value_as_string

    def initialize(self, str_value):
        str_error = ''
        self.file_path = None
        self.layer_name = None
        if str_value:
            if str_value is None:
                str_error = ('Vector Layer Parameter value is None')
                return str_error
            if not isinstance(str_value, str):
                str_error = ('Vector Layer Parameter: {} value as string must be a string and is: {}'
                             .format(self.label, str(type(str_value))))
                return str_error
            value = None
            try:
                value = json.loads(str_value)
            except ValueError as e:
                str_error = str(e)
                return str_error
            if not value:
                return str_error
            if not defs_pars.TAG_FILE_PATH in value:
                str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_FILE_PATH))
                return str_error
            self.file_path = value[defs_pars.TAG_FILE_PATH]
            if not defs_pars.TAG_LAYER_NAME in value:
                str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_NAME))
                return str_error
            self.layer_name = value[defs_pars.TAG_LAYER_NAME]
            if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
                str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
                return str_error
            layer_geometry_type = value[defs_pars.TAG_LAYER_GEOMETRY_TYPE]
            if not isinstance(layer_geometry_type, list):
                str_error = ('Vector Layer Field Name Parameter: {} layer geometry type must be a list and is: {}'
                             .format(self.label, str(type(layer_geometry_type))))
                return str_error
            for i in range(len(layer_geometry_type)):
                str_layer_geometry_type = layer_geometry_type[i]
                if not isinstance(str_layer_geometry_type, str):
                    str_error = ('Vector Layer Field Name Parameter: {} each layer geometry type value in list must be a string and is: {}'
                                 .format(self.label, str(type(str_layer_geometry_type))))
                    return str_error
                if not str_layer_geometry_type in defs_gdal.geometry_type_by_name:
                    str_error = ('Vector Layer Field Name Parameter: {} not valid geometry type: {}'
                                 .format(self.label, str_layer_geometry_type))
                    return str_error
                self.layer_geometry_ogr_wkb_type.append(defs_gdal.geometry_type_by_name[str_layer_geometry_type])
            self.value_as_dict = value
            self.value_as_string = str_value

        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        if self.file_path:
            self.fileComboBox.addItem(self.file_path)
        if self.qgis_iface:
            str_error, self.qgis_layers_by_name = QGISTools.get_vector_layers(self.layer_geometry_ogr_wkb_type)
            if str_error:
                return str_error
            if len(self.qgis_layers_by_name) > 0:
                self.fileComboBox.addItem(defs_qgis.QGIS_PROJECT_TAG)
        self.fileComboBox.setEnabled(True)

        self.layerComboBox.clear()
        self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        # if self.layer_name:
        #     self.layerComboBox.addItem(self.layer_name)
        self.layerComboBox.setEnabled(False)

        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        self.layerComboBox.currentIndexChanged.connect(self.layer_changed)

        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)

        self.addFilePushButton.clicked.connect(self.add_file)
        self.newLayerPushButton.clicked.connect(self.new_layer)
        self.newLayerPushButton.setEnabled(False)
        return str_error

    def layer_changed(self):
        return

    def new_layer(self):
        return
