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
from pyLibGDAL.GpkgTools import GpkgTools
from pyLibGDAL import defs_gdal
from pyLibGDAL.GDALTools import GDALTools

from .Tools import SimpleTextEditDialog


class VectorLayerFieldDialog(QDialog):
    """Employee dialog."""

    def __init__(self,
                 title,
                 label,
                 str_value,
                 domain,
                 qgis_iface,
                 parent=None):
        super().__init__(parent)
        loadUi(os.path.join(os.path.dirname(__file__), 'VectorLayerFieldDialog.ui'), self)
        # loadUi("lib/InstrumentsDialog.ui", self)
        self.label = label
        self.domain = domain
        self.qgis_iface = None
        self.value_as_dict = None
        self.value_as_string = None
        self.file_path = None
        self.layer_name = None
        self.field_name = None
        self.initialize(str_value)

    def add_file(self):
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
        str_error, driver_name = GDALTools.get_driver_name_from_file(file_path)
        if str_error:
            QMessageBox.information(self, 'Information', str_error)
            self.fileComboBox.setCurrentIndex(0)
        return

    def get_value_as_string(self):
        str_error = ''
        str_error = 'kakita del to'
        return str_error, self.value_as_string

    def initialize(self, str_value):
        str_error = ''
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
        self.file_path = None
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        self.file_path = value[defs_pars.TAG_FILE_PATH]
        self.layer_name = None
        if not defs_pars.TAG_LAYER_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_NAME))
            return str_error
        self.layer_name = value[defs_pars.TAG_LAYER_NAME]
        self.field_name = None
        if not defs_pars.TAG_FIELD_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FIELD_NAME))
            return str_error
        self.field_name = value[defs_pars.TAG_FIELD_NAME]
        self.value_as_dict = value
        self.value_as_string = str_value

        self.fileComboBox.clear()
        self.fileComboBox.addItem(defs_pars.NO_COMBO_SELECT)
        if self.file_path:
            self.fileComboBox.addItem(self.file_path)
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
        return str_error

    def layer_changed(self):

        return

    def new_field(self):
        return

    def new_layer(self):
        return
