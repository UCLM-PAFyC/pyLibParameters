# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import sys

from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtWidgets import (QMessageBox, QDialog, QInputDialog, QFileDialog, QLineEdit, QAbstractItemView)
from qgis.PyQt.QtCore import QDir, QFileInfo

from ..Parameter import *

from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools
from pyLibQGIS import defs_qgis
from pyLibQtTools.JsonModel import JsonModel


# from pyLibQGIS.QGISTools import QGISTools


class VectorLayerDialog(QDialog):

    def __init__(self,
                 title,
                 label,
                 str_value,
                 domain,
                 file_mode,
                 mandatory,
                 qgis_iface,
                 settings,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'VectorLayerDialog.ui'), self)
        self.label = label
        self.domain = domain
        self.file_mode = file_mode
        self.mandatory = mandatory
        self.qgis_iface = qgis_iface
        self.settings = settings
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_name = None
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
        str_files = '(*.*)'
        if isinstance(self.domain, list):
            if len(self.domain) > 0:
                str_files = 'Files ('
                for i in range(len(self.domain)):
                    if i > 0:
                        str_files += ' '
                    str_files += ("*" + self.domain[i])
                str_files += ')'
        dlg = QFileDialog()
        dlg.setWindowTitle(title)
        dlg.setDirectory(last_path)
        dlg.setNameFilter(str_files)
        if self.file_mode == defs_pars.FILE_MODE_READ:
            dlg.setFileMode(QFileDialog.ExistingFile)
            # file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
        elif self.file_mode == defs_pars.FILE_MODE_APPEND:
            dlg.setFileMode(QFileDialog.ExistingFile)
            # file_name, aux = QFileDialog.getOpenFileName(self, title, path, str_files)
        elif self.file_mode == defs_pars.FILE_MODE_WRITE:
            dlg.setFileMode(QFileDialog.AnyFile)
            # file_name, aux = QFileDialog.getSaveFileName(self, title, path, str_files)
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
        self.newLayerPushButton.setEnabled(True)
        if not os.path.exists(file_path): # new file
            # if self.layerComboBox.count() > 1:
            #     self.layerComboBox.setEnabled(True)
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
            else:
                layer_name = self.layerComboBox.currentText()
                if layer_name == defs_pars.NO_COMBO_SELECT:
                    str_error = ('No layer selected')
                    return str_error, self.value_as_string
        self.value_as_dict[defs_pars.TAG_FILE_PATH] = file_path
        self.value_as_dict[defs_pars.TAG_LAYER_NAME] = layer_name
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
                str_error = ('Vector Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_FILE_PATH))
                return str_error
            file_name = value[defs_pars.TAG_FILE_PATH]
            if self.file_mode == defs_pars.FILE_MODE_READ or self.file_mode == defs_pars.FILE_MODE_APPEND:
                if not os.path.exists(file_name):
                    msg = ('Not exists file:\n{}'.format(file_name))
                    QMessageBox.information(self, 'Information', msg)
                    file_name = ''
            self.file_path = file_name
            if not defs_pars.TAG_LAYER_NAME in value:
                str_error = ('Vector Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_NAME))
                return str_error
            layer_name = ''
            if file_name:
                layer_name = value[defs_pars.TAG_LAYER_NAME]
            self.layer_name = layer_name
            if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
                str_error = ('Vector Layer Parameter: {} value must contain {}'
                             .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
                return str_error
            layer_geometry_type = value[defs_pars.TAG_LAYER_GEOMETRY_TYPE]
            if not isinstance(layer_geometry_type, list):
                str_error = ('Vector Layer Parameter: {} layer geometry type must be a list and is: {}'
                             .format(self.label, str(type(layer_geometry_type))))
                return str_error
            for i in range(len(layer_geometry_type)):
                str_layer_geometry_type = layer_geometry_type[i]
                if not isinstance(str_layer_geometry_type, str):
                    str_error = (
                        'Vector Layer Parameter: {} each layer geometry type value in list must be a string and is: {}'
                        .format(self.label, str(type(str_layer_geometry_type))))
                    return str_error
                if not str_layer_geometry_type in defs_gdal.geometry_type_by_name:
                    str_error = ('Vector Layer Parameter: {} not valid geometry type: {}'
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
            str_error, self.qgis_layers_by_name = self.QGISTools.get_vector_layers(self.layer_geometry_ogr_wkb_type)
            if str_error:
                return str_error
            if len(self.qgis_layers_by_name) > 0:
                self.fileComboBox.addItem(defs_qgis.QGIS_PROJECT_TAG)
        self.fileComboBox.setEnabled(True)

        self.layerComboBox.clear()
        self.layerComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        self.layerComboBox.setEnabled(False)
        if self.layer_name:
            self.layerComboBox.addItem(self.layer_name)
            self.layerComboBox.setEnabled(True)

        self.addFilePushButton.clicked.connect(self.add_file)
        self.newLayerPushButton.clicked.connect(self.new_layer)
        self.metadataTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.newLayerPushButton.setEnabled(False)

        if self.file_path:
            self.fileComboBox.setCurrentIndex(1)
            self.newLayerPushButton.setEnabled(True)

        if self.layer_name:
            self.layerComboBox.setCurrentIndex(1)

        self.fileComboBox.currentIndexChanged.connect(self.file_changed)
        self.layerComboBox.currentIndexChanged.connect(self.layer_changed)
        return str_error

    def layer_changed(self):
        file_path = self.fileComboBox.currentText()
        self.metadataTreeView.setModel(None)
        if file_path == defs_pars.NO_COMBO_SELECT:
            return
        layer_name = self.layerComboBox.currentText()
        if layer_name == defs_pars.NO_COMBO_SELECT:
            return
        if not layer_name:
            return
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
        if not os.path.exists(file_path): # new file
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

    def new_layer(self):
        title = 'Input name for new layer'
        text, ok = QInputDialog.getText(self, title, 'Layer name',
                                        QLineEdit.Normal)
        # if ok and text != '' and text != str_value:
        if ok:
            value = text.strip()
            if self.layerComboBox.findText(value) == -1:
                self.layerComboBox.addItem(value)
            self.layerComboBox.setCurrentIndex(self.layerComboBox.findText(value))
        if self.layerComboBox.count() > 1:
            self.layerComboBox.setEnabled(True)
        return
