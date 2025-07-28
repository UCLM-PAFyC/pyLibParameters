import os
import sys
import math
import random
import re

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '.'))

import json
import defs_pars
from Parameter import *

class ParametersManager:
    def __init__(self):
        self.parameters = None
        self.parameters_as_list_of_dict = None

    def get_process_arguments(self):
        str_error = ''
        arguments = []
        for parameter_label in self.parameters:
            parameter = self.parameters[parameter_label]
            str_argparser = parameter.argparser.strip()
            parameter_arg_parser = ("--{}".format(str_argparser))
            str_value = str(parameter).strip()
            parameter_value = None
            if isinstance(parameter, BooleanParameter):
                if str_value.casefold() == ('True').casefold():
                    parameter_value = '1' # needed for argument in list of strings
                    # parameter_value = 1
                else:
                    parameter_value = '0' # needed for argument in list of strings
                    # parameter_value = 0
            elif isinstance(parameter, DateParameter):
                # parameter_value = ('\"{}\"'.format(str_value))
                parameter_value = ('{}'.format(str_value))
            elif isinstance(parameter, FileParameter):
                # parameter_value = ('\"{}\"'.format(str_value))
                if parameter.mandatory:
                    if not str_value:
                        str_error += ('For parameter: {} file is not selected'.format(parameter_label))
                        return str_error, arguments
                    if not os.path.exists(str_value):
                        str_error += ('For parameter: {} not exists file:\n{}'.format(parameter_label,
                                                                                      str_value))
                        return str_error, arguments
                    str_value = os.path.normcase(str_value)
                parameter_value = ('{}'.format(str_value))
            elif isinstance(parameter, IntegerParameter):
                # parameter_value = int(str_value)
                parameter_value = str_value # needed for argument in list of strings
            elif isinstance(parameter, PhysicalQuantityParameter):
                str_value = parameter.get_str_value_wihtout_unit()
                parameter_value = str_value # needed for argument in list of strings
                # parameter_value = float(str_value)
            elif isinstance(parameter, RealParameter):
                parameter_value = str_value # needed for argument in list of strings
                # parameter_value = float(str_value)
            elif isinstance(parameter, StringParameter):
                # parameter_value = ('\"{}\"'.format(str_value))
                parameter_value = ('{}'.format(str_value))
            elif isinstance(parameter, RasterLayerParameter):
                # str_value = str_value.replace("\"", "\\\"\"")
                # parameter_value = ('\"{}\"'.format(str_value))
                if parameter.mandatory:
                    if not str_value:
                        str_error += ('For parameter: {} file is not selected'.format(parameter_label))
                        return str_error, arguments
                    if not os.path.exists(str_value):
                        str_error += ('For parameter: {} not exists file:\n{}'.format(parameter_label,
                                                                                      str_value))
                        return str_error, arguments
                    str_value = os.path.normcase(str_value)
                parameter_value = ('{}'.format(str_value))
            elif isinstance(parameter, VectorLayerParameter):
                # str_value = str_value.replace("\"", "\\\"\"")
                # parameter_value = ('\"{}\"'.format(str_value))
                if parameter.mandatory:
                    if not str_value:
                        str_error += ('For parameter: {} file is not selected'.format(parameter_label))
                        return str_error, arguments
                    if not os.path.exists(str_value):
                        str_error += ('For parameter: {} not exists file:\n{}'.format(parameter_label,
                                                                                      str_value))
                        return str_error, arguments
                    str_value = os.path.normcase(str_value)
                parameter_value = ('{}'.format(str_value))
            elif isinstance(parameter, VectorLayerFieldNameParameter):
                # str_value = str_value.replace("\"", "\\\"\"")
                # parameter_value = ('\"{}\"'.format(str_value))
                if parameter.mandatory:
                    if not str_value:
                        str_error += ('For parameter: {} file is not selected'.format(parameter_label))
                        return str_error, arguments
                    if not os.path.exists(str_value):
                        str_error += ('For parameter: {} not exists file:\n{}'.format(parameter_label,
                                                                                      str_value))
                        return str_error, arguments
                    str_value = os.path.normcase(str_value)
                parameter_value = ('{}'.format(str_value))
            if not parameter_value:
                str_error = ('Invalid parameter: {}'.format(parameter.label))
                return str_error, arguments
            arguments.append(parameter_arg_parser)
            arguments.append(parameter_value)
        return str_error, arguments

    def initialize(self, parameters_dictionary_list):
        str_error = ''
        if not isinstance(parameters_dictionary_list, list):
            str_error = ('ParametersManager.initialize\n')
            str_error += ('parameters_dictionary is not a dictionary, is: {}'.format(str(type(str))))
            return str_error
        parameters_count = 0
        parameters = {}
        parameters_as_list_of_dict = []
        for parameter_dict in parameters_dictionary_list:
            if not isinstance(parameter_dict, dict):
                str_error = ('ParametersManager.initialize\n')
                str_error += ('Parameter: {} is not a dictionary, is: {}'.
                              format(str(parameters_count + 1), str(type(str))))
                return str_error
            parameter_fields = {}
            for common_field in defs_pars.parameter_common_fields:
                if not common_field in parameter_dict:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += ("No field {} in parameter: {}".
                                 format(common_field, str(parameters_count + 1)))
                    return str_error
                parameter_fields[common_field] = parameter_dict[common_field]
            parameter_type = parameter_fields[defs_pars.PARAMETER_FIELD_TYPE].lower()
            # original_parameter_type = None
            # if parameter_type in defs_pars.type_group_by_type:
            #     original_parameter_type = parameter_type
            #     parameter_type = defs_pars.type_group_by_type[parameter_type]
            if not parameter_type in defs_pars.parameter_fields_by_type:
                str_error = ('ParametersManager.initialize\n')
                str_error += ("Invalid type: {} parameter: {}".
                             format(parameter_type, str(parameters_count + 1)))
                return str_error
            for another_field in defs_pars.parameter_fields_by_type[parameter_type]:
                if not another_field in parameter_dict:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += ("No field {} in parameter: {}".
                                 format(another_field, str(parameters_count + 1)))
                    return str_error
                parameter_fields[another_field] = parameter_dict[another_field]
            for optional_field in defs_pars.parameter_optional_fields_by_type[parameter_type]:
                if optional_field in parameter_dict:
                    parameter_fields[optional_field] = parameter_dict[optional_field]
            for parameter_field_in_dict in parameter_dict:
                if not parameter_field_in_dict in parameter_fields:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += ("Invalid field {} in parameter: {}".
                                 format(parameter_field_in_dict, str(parameters_count + 1)))
                    return str_error
            parameter = None
            parameter_label = parameter_fields[defs_pars.PARAMETER_FIELD_LABEL]
            parameter_argparser = parameter_fields[defs_pars.PARAMETER_FIELD_ARGPARSER]
            parameter_description = parameter_fields[defs_pars.PARAMETER_FIELD_DESCRIPTION]
            parameter_mandatory = parameter_fields[defs_pars.PARAMETER_FIELD_MANDATORY]
            parameter_output_format = parameter_fields[defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT]
            relative_tolerance = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE
            if defs_pars.PARAMETER_FIELD_TOLERANCE in parameter_fields:
                relative_tolerance = parameter_fields[defs_pars.PARAMETER_FIELD_TOLERANCE]
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            if not parameter_value and parameter_mandatory:
                if defs_pars.PARAMETER_FIELD_TOLERANCE in parameter_fields:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += ("No valud for mandatory parameter: {}".format(parameter_label))
                    return str_error
            if parameter_type.casefold() == defs_pars.PARAMETER_TYPE_BOOLEAN.casefold():
                parameter = BooleanParameter(parameter_label, parameter_argparser, parameter_description,
                                             parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                str_aux_error = parameter.initialize(parameter_value)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type == defs_pars.PARAMETER_TYPE_FILE:
                parameter_file_mode = parameter_fields[defs_pars.PARAMETER_FIELD_FILE_MODE]
                parameter = FileParameter(parameter_label, parameter_argparser, parameter_description,
                                          parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = None
                if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                    parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_file_mode, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_INTEGER.casefold():
                parameter = IntegerParameter(parameter_label, parameter_argparser, parameter_description,
                                             parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_REAL.casefold():
                parameter = RealParameter(parameter_label, parameter_argparser, parameter_description,
                                          parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain, relative_tolerance)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_STRING.casefold():
                parameter = StringParameter(parameter_label, parameter_argparser, parameter_description,
                                            parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = None
                if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                    parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_DATE.casefold():
                parameter = DateParameter(parameter_label, parameter_argparser, parameter_description,
                                            parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_date_format = parameter_fields[defs_pars.PARAMETER_FIELD_DATE_FORMAT]
                str_aux_error = parameter.initialize(parameter_value, parameter_date_format)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_PHYSICAL_QUANTITY.casefold():
                parameter = PhysicalQuantityParameter(parameter_label, parameter_argparser, parameter_description,
                                                      parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                parameter_ui_unit = parameter_fields[defs_pars.PARAMETER_FIELD_QUANTITY_UI_UNIT]
                parameter_computation_unit = parameter_fields[defs_pars.PARAMETER_FIELD_QUANTITY_COMPUTATION_UNIT]
                parameter_output_format_unit = parameter_fields[defs_pars.PARAMETER_FIELD_QUANTITY_OUTPUT_FORMAT_UNIT]
                parameter_ignored_units = []
                if defs_pars.PARAMETER_FIELD_QUANTITY_IGNORED_UNITS in parameter_fields:
                    parameter_ignored_units = parameter_fields[defs_pars.PARAMETER_FIELD_QUANTITY_IGNORED_UNITS]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain,
                                                     parameter_ui_unit,
                                                     parameter_computation_unit,
                                                     parameter_output_format_unit,
                                                     parameter_ignored_units,
                                                     relative_tolerance)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type == defs_pars.PARAMETER_TYPE_RASTER_LAYER:
                parameter_file_mode = parameter_fields[defs_pars.PARAMETER_FIELD_FILE_MODE]
                parameter = RasterLayerParameter(parameter_label, parameter_argparser, parameter_description,
                                                 parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = None
                if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                    parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_file_mode, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type == defs_pars.PARAMETER_TYPE_VECTOR_LAYER:
                parameter_file_mode = parameter_fields[defs_pars.PARAMETER_FIELD_FILE_MODE]
                parameter = VectorLayerParameter(parameter_label, parameter_argparser, parameter_description,
                                                 parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = None
                if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                    parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_file_mode, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type == defs_pars.PARAMETER_TYPE_VECTOR_LAYER_FIELD_NAME:
                parameter_file_mode = parameter_fields[defs_pars.PARAMETER_FIELD_FILE_MODE]
                parameter = VectorLayerFieldNameParameter(parameter_label, parameter_argparser, parameter_description,
                                                          parameter_output_format, parameter_mandatory)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = None
                if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                    parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_file_mode, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error

            str_value = str(parameter)
            parameters[parameter_label] = parameter
            parameters_as_list_of_dict.append(parameter_dict)
            parameters_count += 1
        self.parameters = parameters
        self.parameters_as_list_of_dict = parameters_as_list_of_dict
        return str_error

    def set_value(self, label, str_value):
        str_error = ''
        if not label in self.parameters:
            str_error = ('Not exists parameter: {}'.format(label))
        parameter = self.parameters[label]
        parameter_str_value = str(parameter)
        if str_value.casefold() == parameter_str_value.casefold():
            return str_error
        value = None
        if isinstance(parameter, BooleanParameter):
            value = True
            if str_value.casefold() == ('False').casefold():
                value = False
            str_error = parameter.set_value(value)
            if str_error:
                return str_error
        elif isinstance(parameter, DateParameter):
            str_error = parameter.set_value(str_value, parameter.date_format)
            if str_error:
                return str_error
            value = str_value
        elif isinstance(parameter, FileParameter):
            str_error = parameter.set_value(str_value)
            if str_error:
                return str_error
            value = str_value
        elif isinstance(parameter, IntegerParameter):
            str_error = parameter.set_value(str_value)
            if str_error:
                return str_error
            value = str_value
        elif isinstance(parameter, PhysicalQuantityParameter):
            str_values = str_value.split()
            str_value = str_values[0]
            value = float(str_value)
            str_error = parameter.set_value(str_value)
            if str_error:
                return str_error
        elif isinstance(parameter, RealParameter):
            value = float(str_value)
            str_error = parameter.set_value(str_value)
            if str_error:
                return str_error
        elif isinstance(parameter, StringParameter):
            str_error = parameter.set_value(str_value)
            if str_error:
                return str_error
            value = str_value
        elif isinstance(parameter, VectorLayerParameter):
            value = json.loads(str_value)
            str_error = parameter.set_value(value)
            if str_error:
                return str_error
        elif isinstance(parameter, VectorLayerFieldNameParameter):
            value = json.loads(str_value)
            str_error = parameter.set_value(value)
            if str_error:
                return str_error
        elif isinstance(parameter, RasterLayerParameter):
            value = json.loads(str_value)
            str_error = parameter.set_value(value)
            if str_error:
                return str_error
        else:
            str_error = ('Not found parameter: {}'.format(label))
            return str_error
        for i in range(len(self.parameters_as_list_of_dict)):
            parameter_label = self.parameters_as_list_of_dict[i][defs_pars.PARAMETER_FIELD_LABEL]
            if label.casefold() == parameter_label.casefold():
                self.parameters_as_list_of_dict[i][defs_pars.PARAMETER_FIELD_VALUE] = value
                break
        return str_error