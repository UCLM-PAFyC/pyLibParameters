# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys

from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtWidgets import (QMessageBox, QDialog, QFileDialog, QAbstractItemView)
from qgis.PyQt.QtCore import QDir, QFileInfo, Qt

from ..Parameter import *

from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
from pyLibQtTools.JsonModel import JsonModel
from pyLibQtTools.CheckableComboBox import CheckableComboBox
# from pyLibQGIS.QGISTools import QGISTools

class LayerSetDialog(QDialog):

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
        loadUi(os.path.join(os.path.dirname(__file__), 'LayerSetDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_names_selected = []
        self.file_path_selected = None
        self.layer_names = []
        self.layer_geometry_ogr_wkb_type = []
        self.layer_type_by_name = {}
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
        self.layerComboBox.clear()
        # self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.layerComboBox.setEnabled(False)
        self.newLayerPushButton.setEnabled(False)
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
        for i in range(len(self.layer_names)):
            layer_name = self.layer_names[i]
            self.layerComboBox.addItem(layer_name)
            index = self.layerComboBox.findText(layer_name)
            model = self.layerComboBox.model()
            item = model.item(index)
            item.setCheckState(Qt.Unchecked)
            if file_path == self.file_path_selected:
                if layer_name in self.layer_names_selected:
                    item.setCheckState(Qt.Checked)
        self.layerComboBox.setEnabled(True)
        return

    def get_value_as_string(self):
        str_error = ''
        str_value = ''
        file_path = ''
        layer_names = None
        file_path = self.fileComboBox.currentText()
        if file_path == defs_pars.NO_COMBO_SELECT:
            if self.mandatory:
                str_error = ('No file selected')
                return str_error, self.value_as_string
            else:
                file_path = ''
        else:
            layer_names = self.layerComboBox.get_checked_texts()
        self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
        self.value_as_dict[defs_pars.TAG_LAYER_NAMES] = layer_names
        self.value_as_string = json.dumps(self.value_as_dict)
        return str_error, self.value_as_string

    def initialize(self, str_value):
        str_error = ''
        self.file_path = None
        self.layer_name = None
        self.layer_names = []
        self.layer_names_selected = []
        self.layer_type_by_name = {}
        if str_value:
            if str_value is None:
                str_error = ('Layer Set Parameter value is None')
                return str_error
            if not isinstance(str_value, str):
                str_error = ('Layer Set Parameter: {} value as string must be a string and is: {}'
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
                str_error = ('Layer Set Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_FILE_PATH))
                return str_error
            file_name = value[defs_pars.TAG_FILE_PATH]
            if not os.path.exists(file_name):
                msg = ('Not exists file:\n{}'.format(file_name))
                QMessageBox.information(self, 'Information', msg)
                file_name = ''
            self.file_path = file_name
            self.file_path_selected = file_name
            if not defs_pars.TAG_LAYER_NAMES in value:
                str_error = ('Layer Set Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_NAMES))
                return str_error
            layer_names = None
            if file_name:
                layer_names = value[defs_pars.TAG_LAYER_NAMES]
            self.layer_names_selected = layer_names
            self.value_as_dict = value
            self.value_as_string = str_value
        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        if self.file_path:
            self.fileComboBox.addItem(self.file_path)
        self.fileComboBox.setEnabled(True)

        self.layerComboBox = CheckableComboBox()
        self.gridLayout.addWidget(self.layerComboBox,1,1,1,1)

        self.layerComboBox.clear()
        self.layerComboBox.setEnabled(False)

        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        self.layerComboBox.currentIndexChanged.connect(self.layer_changed)

        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)
            self.file_changed()

        self.addFilePushButton.clicked.connect(self.add_file)
        self.newLayerPushButton.clicked.connect(self.new_layer)
        self.newLayerPushButton.setEnabled(False)
        self.metadataTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return str_error

    def layer_changed(self):
        file_path = self.fileComboBox.currentText()
        self.metadataTreeView.setModel(None)
        if file_path == defs_pars.NO_COMBO_SELECT:
            return
        layer_name = self.layerComboBox.currentText()
        # if layer_name == defs_pars.NO_COMBO_SELECT:
        #     return
        if not layer_name:
            return
        if self.layer_type_by_name[layer_name] == defs_gdal.GDAL_ALIAS_VECTOR:
            str_error, metadata = GDALTools.ogrinfo_as_json(file_path, layer_name)
        else:
            str_error, metadata = GDALTools.gdalinfo_as_json(file_path, layer_name)
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
        return

    def new_layer(self):
        return
