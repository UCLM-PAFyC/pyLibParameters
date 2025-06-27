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

    def initialize(self, parameters_dictionary_list):
        str_error = ''
        if not isinstance(parameters_dictionary_list, list):
            str_error = ('ParametersManager.initialize\n')
            str_error += ('parameters_dictionary is not a dictionary, is: {}'.format(str(type(str))))
            return str_error
        parameters_count = 0
        parameters = {}
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
            parameter_output_format = parameter_fields[defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT]
            relative_tolerance = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE
            if defs_pars.PARAMETER_FIELD_TOLERANCE in parameter_fields:
                relative_tolerance = parameter_fields[defs_pars.PARAMETER_FIELD_TOLERANCE]
            if parameter_type.casefold() == defs_pars.PARAMETER_TYPE_BOOLEAN.casefold():
                parameter = BooleanParameter(parameter_label, parameter_argparser, parameter_description,
                                             parameter_output_format)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                str_aux_error = parameter.initialize(parameter_value)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type == defs_pars.PARAMETER_TYPE_FILE:
                parameter_file_mode = parameter_fields[defs_pars.PARAMETER_FIELD_FILE_MODE]
                parameter = FileParameter(parameter_label, parameter_argparser, parameter_description,
                                          parameter_output_format)
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
                                             parameter_output_format)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_REAL.casefold():
                parameter = RealParameter(parameter_label, parameter_argparser, parameter_description,
                                          parameter_output_format)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
                str_aux_error = parameter.initialize(parameter_value, parameter_domain, relative_tolerance)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_STRING.casefold():
                parameter = StringParameter(parameter_label, parameter_argparser, parameter_description,
                                            parameter_output_format)
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
                                            parameter_output_format)
                parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
                parameter_date_format = parameter_fields[defs_pars.PARAMETER_FIELD_DATE_FORMAT]
                str_aux_error = parameter.initialize(parameter_value, parameter_date_format)
                if str_aux_error:
                    str_error = ('ParametersManager.initialize\n')
                    str_error += str_aux_error
                    return str_error
            elif parameter_type.casefold() == defs_pars.PARAMETER_TYPE_PHYSICAL_QUANTITY.casefold():
                parameter = PhysicalQuantityParameter(parameter_label, parameter_argparser, parameter_description,
                                                      parameter_output_format)
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
            str_value = str(parameter)
            parameters[parameter_label] = parameter
            parameters_count += 1
        self.parameters = parameters
        return str_error
