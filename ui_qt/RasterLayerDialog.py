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
                             QDialogButtonBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
                             QAbstractItemView)
from PyQt5.QtCore import QDir, QFileInfo, QFile, QSize, Qt, QDate

import defs_pars
from Parameter import *
from .ParameterDialog import ParameterDialog

from pyLibCRSs import CRSsDefines as defs_crs
from pyLibCRSs.CRSsTools import CRSsTools
from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
# from pyLibQGIS.QGISTools import QGISTools
from pyLibQtTools.JsonModel import JsonModel



from pyLibQtTools.Tools import SimpleTextEditDialog


class RasterLayerDialog(QDialog):

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
        loadUi(os.path.join(os.path.dirname(__file__), 'RasterLayerDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_index = None
        self.scale = None
        self.offset = None
        self.qgis_layers_by_name = {}
        self.QGISTools = None
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
        title = "Select Raster File"
        dlg = QFileDialog()
        dlg.setDirectory(last_path)
        # dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setNameFilter("Raster File (*.*)")
        if dlg.exec_():
            file_names = dlg.selectedFiles()
            file_name = file_names[0]
        else:
            return
        if file_name:
            str_error, is_vector = GDALTools.is_raster(file_name)
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
        self.scalePushButton.setEnabled(False)
        self.offsetPushButton.setEnabled(False)
        self.metadataTreeView.setModel(None)
        if file_path == defs_pars.NO_COMBO_SELECT:
            str_scale = str(eval(defs_pars.SCALE_STRING_FORMAT.format(defs_pars.SCALE_DEFAULT_VALUE)))
            self.scaleLineEdit.setText(str_scale)
            str_offset = str(eval(defs_pars.OFFSET_STRING_FORMAT.format(defs_pars.OFFSET_DEFAULT_VALUE)))
            self.offsetLineEdit.setText(str_offset)
            return
        current_position = 0
        if file_path in self.qgis_layers_by_name:
            layer_name = file_path
            str_error, raster_count = self.QGISTools.get_raster_band_count(layer_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
            str_error, file_path = self.QGISTools.get_file_path(layer_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
                return
        else:
            str_error, raster_count = GDALTools.get_raster_count(file_path)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
                return
        for i in range(raster_count):
            self.layerComboBox.addItem(str(i + 1))
            if self.layer_index == (i + 1):
                current_position = i + 1
        str_scale = str(eval(defs_pars.SCALE_STRING_FORMAT.format(self.scale)))
        self.scaleLineEdit.setText(str_scale)
        str_offset = str(eval(defs_pars.OFFSET_STRING_FORMAT.format(self.offset)))
        self.offsetLineEdit.setText(str_offset)
        str_error, metadata = GDALTools.gdalinfo_as_json(file_path)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
            return
        metadata_dict = json.loads(metadata)
        model = JsonModel()
        self.metadataTreeView.setModel(model)
        self.metadataTreeView.setAlternatingRowColors(True)
        model.load(metadata_dict)
        self.metadataTreeView.resizeColumnToContents(0)
        self.layerComboBox.setEnabled(True)
        self.layerComboBox.setCurrentIndex(current_position)
        self.scalePushButton.setEnabled(True)
        self.offsetPushButton.setEnabled(True)
        return

    def get_value_as_string(self):
        str_error = ''
        layer_index = None
        scale = None
        offset = None
        file_path = self.fileComboBox.currentText()
        if file_path == defs_pars.NO_COMBO_SELECT:
            if self.mandatory:
                str_error = ('No file selected')
                return str_error, self.value_as_string
            else:
                file_path = ''
        else:
            if not os.path.isfile(file_path):
                str_error, file_path = self.QGISTools.get_file_path(file_path)
                if str_error:
                    return str_error, self.value_as_string
            str_layer_index = self.layerComboBox.currentText()
            if str_layer_index == defs_pars.NO_COMBO_SELECT:
                if self.mandatory:
                    str_error = ('No layer index selected')
                    return str_error, self.value_as_string
                else:
                    file_path = ''
                    layer_name = None
            layer_index = int(str_layer_index)
            str_scale = self.scaleLineEdit.text()
            scale = float(str_scale)
            str_offset = self.offsetLineEdit.text()
            offset = float(str_offset)
        self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
        self.value_as_dict[defs_pars.TAG_LAYER_INDEX] = layer_index
        self.value_as_dict[defs_pars.TAG_SCALE] = scale
        self.value_as_dict[defs_pars.TAG_OFFSET] = offset
        self.value_as_string = json.dumps(self.value_as_dict)
        return str_error, self.value_as_string

    def initialize(self, str_value):
        str_error = ''
        if self.qgis_iface:
            from pyLibQGIS.QGISTools import QGISTools
            self.QGISTools = QGISTools
        self.file_path = None
        self.layer_name = None
        if str_value:
            if str_value is None:
                str_error = ('Raster Layer Parameter value is None')
                return str_error
            if not isinstance(str_value, str):
                str_error = ('Raster Layer Parameter: {} value as string must be a string and is: {}'
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
                str_error = ('Raster Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_FILE_PATH))
                return str_error
            self.file_path = value[defs_pars.TAG_FILE_PATH]
            if not defs_pars.TAG_LAYER_INDEX in value:
                str_error = ('Raster Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_INDEX))
                return str_error
            self.layer_index = value[defs_pars.TAG_LAYER_INDEX]
            if not defs_pars.TAG_SCALE in value:
                str_error = ('Raster Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_SCALE))
                return str_error
            scale = value[defs_pars.TAG_SCALE]
            if not isinstance(scale, float):
                str_error = ('Raster Layer Parameter: {} scale must be a float and is: {}'
                             .format(self.label, str(type(scale))))
                return str_error
            self.scale = scale
            if not defs_pars.TAG_OFFSET in value:
                str_error = ('Raster Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_OFFSET))
                return str_error
            offset = value[defs_pars.TAG_OFFSET]
            if not isinstance(offset, float):
                str_error = ('Raster Layer Parameter: {} offset must be a float and is: {}'
                             .format(self.label, str(type(offset))))
                return str_error
            self.offset = offset
            self.value_as_dict = value
            self.value_as_string = str_value
        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        if self.file_path:
            self.fileComboBox.addItem(self.file_path)
        if self.qgis_iface:
            str_error, self.qgis_layers_by_name = self.QGISTools.get_raster_layers()
            if str_error:
                return str_error
            for qgis_raster_layer_name in self.qgis_layers_by_name:
                self.fileComboBox.addItem(qgis_raster_layer_name)
        self.fileComboBox.setEnabled(True)

        self.layerComboBox.clear()
        self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        # if self.layer_name:
        #     self.layerComboBox.addItem(self.layer_name)
        self.layerComboBox.setEnabled(False)

        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        self.layerComboBox.currentIndexChanged.connect(self.layer_changed)

        self.addFilePushButton.clicked.connect(self.add_file)
        self.newLayerPushButton.clicked.connect(self.new_layer)
        self.newLayerPushButton.setEnabled(False)
        self.scalePushButton.clicked.connect(self.select_scale)
        self.offsetPushButton.clicked.connect(self.select_offset)
        str_scale = str(eval(defs_pars.SCALE_STRING_FORMAT.format(defs_pars.SCALE_DEFAULT_VALUE)))
        self.scaleLineEdit.setText(str_scale)
        str_offset = str(eval(defs_pars.OFFSET_STRING_FORMAT.format(defs_pars.OFFSET_DEFAULT_VALUE)))
        self.offsetLineEdit.setText(str_offset)
        self.scalePushButton.setEnabled(False)
        self.offsetPushButton.setEnabled(False)
        self.metadataTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)

        return str_error

    def layer_changed(self):
        str_layer_index = self.layerComboBox.currentText()
        self.newLayerPushButton.setEnabled(False)
        self.scalePushButton.setEnabled(False)
        self.offsetPushButton.setEnabled(False)
        if str_layer_index == defs_pars.NO_COMBO_SELECT:
            str_scale = str(eval(defs_pars.SCALE_STRING_FORMAT.format(defs_pars.SCALE_DEFAULT_VALUE)))
            self.scaleLineEdit.setText(str_scale)
            str_offset = str(eval(defs_pars.OFFSET_STRING_FORMAT.format(defs_pars.OFFSET_DEFAULT_VALUE)))
            self.offsetLineEdit.setText(str_offset)
            return
        self.scalePushButton.setEnabled(True)
        self.offsetPushButton.setEnabled(True)
        return

    def new_layer(self):
        return

    def select_scale(self):
        str_value = self.scaleLineEdit.text()
        title = "Target value = scale * DL + offset"
        msg = ("Input scale:")
        text, ok = QInputDialog.getText(self, title, msg,
                                        QLineEdit.Normal, str_value)
        if ok:
            real_value = None
            try:
                real_value = float(text)
            except ValueError:
                msg = ('Value must be a real number in domain')
                QMessageBox.information(self, 'Information', msg)
                return
            str_scale = str(eval(defs_pars.SCALE_STRING_FORMAT.format(real_value)))
            self.scaleLineEdit.setText(str_scale)
        return

    def select_offset(self):
        str_value = self.offsetLineEdit.text()
        title = "Target value = scale * DL + offset"
        msg = ("Input offset:")
        text, ok = QInputDialog.getText(self, title, msg,
                                        QLineEdit.Normal, str_value)
        if ok:
            real_value = None
            try:
                real_value = float(text)
            except ValueError:
                msg = ('Value must be a real number in domain')
                QMessageBox.information(self, 'Information', msg)
                return
            str_offset = str(eval(defs_pars.SCALE_STRING_FORMAT.format(real_value)))
            self.offsetLineEdit.setText(str_offset)
        return
