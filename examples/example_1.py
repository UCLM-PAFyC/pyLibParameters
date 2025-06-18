import os
import sys
import math
import random
import re

import defs_pars

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

import json
from Parameter import *

def test_1(input_file_name):
    str_error = ''
    with open(input_file_name, 'r') as file:
        json_content = json.load(file)
    if not defs_pars.PARAMETERS_TAG in json_content:
        str_error = ("No {} in json project file:\n{}".format(defs_pars.PARAMETERS_TAG,
                                                              input_file_name))
        return str_error
    parameters_count = 0
    parameters = {}
    for parameter_dict in json_content[defs_pars.PARAMETERS_TAG]:
        parameter_fields = {}
        for common_field in defs_pars.parameter_common_fields:
            if not common_field in parameter_dict:
                str_error = ("No field {} in parameter: {} in json project file:\n{}".
                             format(common_field, str(parameters_count + 1), input_file_name))
                return str_error
            parameter_fields[common_field] = parameter_dict[common_field]
        parameter_tye = parameter_fields[defs_pars.PARAMETER_FIELD_TYPE].lower()
        if not parameter_tye in defs_pars.parameter_fields_by_type:
            str_error = ("Invalid type: {} parameter: {} in json project file:\n{}".
                         format(parameter_tye, str(parameters_count + 1), input_file_name))
            return str_error
        for another_field in defs_pars.parameter_fields_by_type[parameter_tye]:
            if not another_field in parameter_dict:
                str_error = ("No field {} in parameter: {} in json project file:\n{}".
                             format(another_field, str(parameters_count + 1), input_file_name))
                return str_error
            parameter_fields[another_field] = parameter_dict[another_field]
        for optional_field in defs_pars.parameter_optional_fields_by_type[parameter_tye]:
            if optional_field in parameter_dict:
                parameter_fields[optional_field] = parameter_dict[optional_field]
        for parameter_field_in_dict in parameter_dict:
            if not parameter_field_in_dict in parameter_fields:
                str_error = ("Invalid field {} in parameter: {} in json project file:\n{}".
                             format(parameter_field_in_dict, str(parameters_count + 1), input_file_name))
                return str_error
        parameter = None
        parameter_label = parameter_fields[defs_pars.PARAMETER_FIELD_LABEL]
        parameter_description = parameter_fields[defs_pars.PARAMETER_FIELD_DESCRIPTION]
        parameter_output_format = parameter_fields[defs_pars.PARAMETER_FIELD_OUTPUT_FORMAT]
        relative_tolerance = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE
        if defs_pars.PARAMETER_FIELD_TOLERANCE in parameter_fields:
            relative_tolerance = parameter_fields[defs_pars.PARAMETER_FIELD_TOLERANCE]
        if parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_BOOLEAN_TAG.casefold():
            parameter = BooleanParameter(parameter_label, parameter_description, parameter_output_format)
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            str_error = parameter.initialize(parameter_value)
            if str_error:
                return str_error
        elif (parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_OPEN_FILE_TAG.casefold()
              or parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_SAVE_FILE_TAG.casefold()):
            file_open = False
            file_save = True
            if parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_OPEN_FILE_TAG.casefold():
                file_open = True
                file_save = False
            parameter = FileParameter(parameter_label, parameter_description, parameter_output_format,
                                      file_open, file_save)
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            parameter_domain = None
            if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
            str_error = parameter.initialize(parameter_value, parameter_domain)
            if str_error:
                return str_error
        elif parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_INTEGER_TAG.casefold():
            parameter = IntegerParameter(parameter_label, parameter_description, parameter_output_format)
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
            str_error = parameter.initialize(parameter_value, parameter_domain)
            if str_error:
                return str_error
        elif parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_REAL_TAG.casefold():
            parameter = RealParameter(parameter_label, parameter_description, parameter_output_format)
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
            str_error = parameter.initialize(parameter_value, parameter_domain, relative_tolerance)
            if str_error:
                return str_error
        elif parameter_tye.casefold() == defs_pars.PARAMETER_TYPE_STRING_TAG.casefold():
            parameter = StringParameter(parameter_label, parameter_description, parameter_output_format)
            parameter_value = parameter_fields[defs_pars.PARAMETER_FIELD_VALUE]
            parameter_domain = None
            if defs_pars.PARAMETER_FIELD_DOMAIN in parameter_fields:
                parameter_domain = parameter_fields[defs_pars.PARAMETER_FIELD_DOMAIN]
            str_error = parameter.initialize(parameter_value, parameter_domain)
            if str_error:
                return str_error
        str_value = str(parameter)
        parameters[parameter_label] = parameter
        parameters_count += 1

        yo = 1
    return str_error


def main():
    input_file_name = 'E:/dev/python/lib/pyLibParameters/examples/process_crop_water_stress_using_cwsi_input_shp.json'
    # input_file_name = 'E:/dev/python/lib/pyLibParameters/examples/process_crop_water_stress_using_cwsi_input_gpkg.json'
    str_error = test_1(input_file_name)
    if str_error:
        print(f"Processing test_1: error:\n\t{str_error}")
        return


if __name__ == '__main__':
    main()


