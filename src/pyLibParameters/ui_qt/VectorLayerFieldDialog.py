# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys

from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtWidgets import (QMessageBox, QDialog, QFileDialog, QAbstractItemView)
from qgis.PyQt.QtCore import QDir, QFileInfo

from src.pyLibParameters.Parameter import *

from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
# from pyLibQGIS.QGISTools import QGISTools
from pyLibQtTools.JsonModel import JsonModel

class VectorLayerFieldDialog(QDialog):
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
        loadUi(os.path.join(os.path.dirname(__file__), 'VectorLayerFieldDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_name = None
        self.field_name = None
        self.layer_geometry_ogr_wkb_type = []
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

    def field_changed(self):
        return

    def file_changed(self):
        file_path = self.fileComboBox.currentText()
        self.layerComboBox.clear()
        self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.layerComboBox.setEnabled(False)
        self.fieldComboBox.clear()
        self.fieldComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.fieldComboBox.setEnabled(False)
        self.newLayerPushButton.setEnabled(False)
        self.newFieldPushButton.setEnabled(False)
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
                str_error, geometry_type = GDALTools.get_layer_geometry_type(file_path, layer_name)
                if str_error:
                    QMessageBox.information(self, 'Information', str_error)
                    return
                if geometry_type in self.layer_geometry_ogr_wkb_type:
                    if self.layer_name:
                        if layer_name.casefold() == self.layer_name.casefold():
                            current_position = i + 1
                    self.layerComboBox.addItem(layer_name)
        self.layerComboBox.setEnabled(True)
        self.layerComboBox.setCurrentIndex(current_position)
        return

    def get_value_as_string(self):
        str_error = ''
        layer_name = ''
        field_name = ''
        file_path = self.fileComboBox.currentText()
        if file_path == defs_pars.NO_COMBO_SELECT:
            if self.mandatory:
                str_error = ('No file selected')
                return str_error, self.value_as_string
            else:
                file_path = ''
        else:
            if file_path == defs_qgis.QGIS_PROJECT_TAG:
                layer_name = self.layerComboBox.currentText()
                if layer_name == defs_pars.NO_COMBO_SELECT:
                    str_error = ('No layer selected')
                    return str_error, self.value_as_string
                else:
                    str_error, file_path = self.QGISTools.get_file_path(layer_name)
                    if str_error:
                        return str_error, self.value_as_string
                    str_error, layer_name = self.QGISTools.get_layer_name(layer_name)
                    if str_error:
                        return str_error, self.value_as_string
                    field_name = self.fieldComboBox.currentText()
                    if field_name == defs_pars.NO_COMBO_SELECT:
                        str_error = ('No field selected')
                        return str_error, self.value_as_string
            else:
                layer_name = self.layerComboBox.currentText()
                if layer_name == defs_pars.NO_COMBO_SELECT:
                    str_error = ('No layer selected')
                    return str_error, self.value_as_string
                else:
                    field_name = self.fieldComboBox.currentText()
                    if field_name == defs_pars.NO_COMBO_SELECT:
                        str_error = ('No field selected')
                        return str_error, self.value_as_string
        self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
        self.value_as_dict[defs_pars.TAG_LAYER_NAME] = layer_name
        self.value_as_dict[defs_pars.TAG_FIELD_NAME] = field_name
        self.value_as_string = json.dumps(self.value_as_dict)
        return str_error, self.value_as_string

    def initialize(self, str_value):
        str_error = ''
        if self.qgis_iface:
            from pyLibQGIS.QGISTools import QGISTools
            self.QGISTools = QGISTools
        self.file_path = None
        self.layer_name = None
        self.field_name = None
        if str_value:
            if str_value is None:
                str_error = ('Vector Layer Field Name Parameter value is None')
                return str_error
            if not isinstance(str_value, str):
                str_error = ('Vector Layer Field Name Parameter: {} value as string must be a string and is: {}'
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
            file_name = value[defs_pars.TAG_FILE_PATH]
            if not os.path.exists(file_name):
                msg = ('Not exists file:\n{}'.format(file_name))
                QMessageBox.information(self, 'Information', msg)
                file_name = ''
            self.file_path = file_name
            if not defs_pars.TAG_LAYER_NAME in value:
                str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_NAME))
                return str_error
            layer_name = ''
            if file_name:
                layer_name = value[defs_pars.TAG_LAYER_NAME]
            self.layer_name = layer_name
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
            if not defs_pars.TAG_FIELD_NAME in value:
                str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_FIELD_NAME))
                return str_error
            field_name = ''
            if file_name and layer_name:
                field_name = value[defs_pars.TAG_FIELD_NAME]
            self.field_name = field_name
            self.value_as_dict = value
            self.value_as_string = str_value
        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        if self.file_path:
            self.fileComboBox.addItem(self.file_path)
        if self.qgis_iface:
            str_error, self.qgis_layers_by_name = self.QGISTools.get_vector_layers(self.layer_geometry_ogr_wkb_type)
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

        self.fieldComboBox.clear()
        self.fieldComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        # if field_name:
        #     self.fieldComboBox.addItem(field_name)
        self.fieldComboBox.setEnabled(False)

        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        self.layerComboBox.currentIndexChanged.connect(self.layer_changed)
        self.fieldComboBox.currentIndexChanged.connect(self.field_changed)

        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)

        self.addFilePushButton.clicked.connect(self.add_file)
        self.newLayerPushButton.clicked.connect(self.new_layer)
        self.newFieldPushButton.clicked.connect(self.new_field)
        self.newLayerPushButton.setEnabled(False)
        self.newFieldPushButton.setEnabled(False)
        self.metadataTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return str_error

    def layer_changed(self):
        file_path = self.fileComboBox.currentText()
        self.fieldComboBox.clear()
        self.fieldComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.fieldComboBox.setEnabled(False)
        self.newFieldPushButton.setEnabled(False)
        self.metadataTreeView.setModel(None)
        layer_name = self.layerComboBox.currentText()
        if not layer_name or layer_name == defs_pars.NO_COMBO_SELECT:
            return
        current_position = 0
        if file_path == defs_qgis.QGIS_PROJECT_TAG:
            str_error, field_names = self.QGISTools.get_vector_layer_field_names(self.qgis_layers_by_name[layer_name])
        else:
            str_error, field_names = GDALTools.get_layer_field_names(file_path, layer_name)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        if len(field_names) == 0:
            str_error = ('There are no fields in layer: {}\nin file:\n{}'.format(layer_name, file_path))
            QMessageBox.information(self, 'Information', str_error)
            self.layerComboBox.setCurrentIndex(0)
        for i in range(len(field_names)):
            field_name = field_names[i]
            if self.field_name:
                if field_name.casefold() == self.field_name.casefold():
                    current_position = i + 1
            self.fieldComboBox.addItem(field_name)
        self.fieldComboBox.setEnabled(True)
        self.fieldComboBox.setCurrentIndex(current_position)
        if file_path == defs_qgis.QGIS_PROJECT_TAG:
            str_error, file_path = self.QGISTools.get_file_path(layer_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
                return
            str_error, layer_name = self.QGISTools.get_layer_name(layer_name)
            if str_error:
                QMessageBox.information(self, 'Information', str_error)
                self.fileComboBox.setCurrentIndex(0)
                return
        str_error, metadata = GDALTools.ogrinfo_as_json(file_path, layer_name)
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

    def new_field(self):
        return

    def new_layer(self):
        return
