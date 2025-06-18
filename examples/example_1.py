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
from ParametersManager import ParametersManager

def test_1(input_file_name):
    str_error = ''
    with open(input_file_name, 'r') as file:
        json_content = json.load(file)
    if not defs_pars.PARAMETERS in json_content:
        str_error = ("No {} in json project file:\n{}".format(defs_pars.PARAMETERS,
                                                              input_file_name))
        return str_error
    parameters_dictionary_list = json_content[defs_pars.PARAMETERS]
    parameters_manager = ParametersManager()
    str_error = parameters_manager.initialize(parameters_dictionary_list)
    if str_error:
        str_error = ("For json project file:\n{}\nError:\n{}".
                     format(input_file_name, str_error))
        return str_error
    return str_error


def main():
    input_file_name = 'E:/dev/python/lib/pyLibParameters/examples/process_crop_water_stress_using_cwsi_input_shp.json'
    # input_file_name = 'E:/dev/python/lib/pyLibParameters/examples/process_crop_water_stress_using_cwsi_input_gpkg.json'
    str_error = test_1(input_file_name)
    if str_error:
        print(f"Processing test_1: error:\n\t{str_error}")
        return
    yo = 1


if __name__ == '__main__':
    main()


