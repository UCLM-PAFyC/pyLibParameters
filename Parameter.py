# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import math
import defs_pars
import pathlib
import datetime

import defs_pars
import json

#
# from pint import UnitRegistry
# ureg = UnitRegistry()
from pint.util import UnitsContainer


class Parameter:
    def __init__(self, label, argparser, description, output_format, mandatory, output, enabled = True):
        self.label = label
        self.argparser = argparser
        self.description = description
        self.output_format = output_format
        self.value = None
        self.mandatory = mandatory
        self.output = output
        self.enabled = enabled

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def __str__(self):
        str_value = "None"
        if self.value:
            if isinstance(self.value, dict):
                str_value = json.dumps(self.value)
            elif not isinstance(self.value, str):
                str_value = str(eval(self.output_format.format(self.value)))
            else:
                str_value = self.output_format.format(self.value)
                # str_value = self.value
        return str_value

    def __unicode__(self):
        str_value = "None"
        if self.value:
            if not isinstance(self.value, str):
                str_value = str(eval(self.output_format.format(self.value)))
            else:
                str_value = self.value
        return str_value

    def __repr__(self):
        str_value = "None"
        if self.value:
            if not isinstance(self.value, str):
                str_value = str(eval(self.output_format.format(self.value)))
            else:
                str_value = self.value
        return str_value


class BooleanParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value):
        return self.set_value(value)

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Boolean Parameter value is None')
            return str_error
        if not isinstance(value, bool):
            int_value = None
            try:
                int_value = int(value)
            except ValueError:
                str_error = ('Boolean Parameter: {} value must be a boolean or a number (0/1) and is: {}'.
                             format(self.label, str(type(value))))
                return str_error
            if int_value == 0:
                value = False
            elif int_value == 1:
                value = True
            else:
                str_error = ('Boolean Parameter: {} value must be a boolean or an integer (0/1) and is: {}'.
                             format(self.label, str(type(value))))
                return str_error
        self.value = value
        return str_error

    def __str__(self):
        str_value = 'True'
        if not self.value:
            str_value = 'False'
        return str(eval(self.output_format.format(str_value)))

    def __unicode__(self):
        str_value = 'True'
        if not self.value:
            str_value = 'False'
        return str(eval(self.output_format.format(str_value)))

    def __repr__(self):
        str_value = 'True'
        if not self.value:
            str_value = 'False'
        return str(eval(self.output_format.format(str_value)))


class DateParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value, date_format):
        str_error = ''
        str_date_format = date_format
        if str_date_format:
            if not isinstance(str_date_format, str):
                try:
                    str_date_format = str(str_date_format)
                except ValueError:
                    str_error = (
                        'Date Parameter: {} date format must be a string and is: {}'.format(self.label, str(type(date_format))))
                    return str_error
        date_value = None
        str_value = value
        if str_value:
            if not isinstance(str_value, str):
                try:
                    str_value = str(str_value)
                except ValueError:
                    str_error = (
                        'Date Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                    return str_error
            try:
                date_value = datetime.datetime.strptime(str_value, str_date_format).date()
            except ValueError:
                str_error = ('Date Parameter: {} value: {} is not valid for date format: {}'.format(self.label,value, date_format))
                return str_error
        self.value = date_value
        self.date_format = str_date_format
        return str_error

    def set_value(self, value, date_format = None):
        str_error = ''
        str_date_format = self.date_format
        if date_format:
            str_date_format = date_format
            if str_date_format:
                if not isinstance(str_date_format, str):
                    try:
                        str_date_format = str(str_date_format)
                    except ValueError:
                        str_error = (
                            'Date Parameter: {} date format must be a string and is: {}'
                            .format(self.label, str(type(date_format))))
                        return str_error
        date_value = None
        str_value = value
        if str_value:
            if not isinstance(str_value, str):
                try:
                    str_value = str(str_value)
                except ValueError:
                    str_error = (
                        'Date Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                    return str_error
            try:
                date_value = datetime.datetime.strptime(str_value, str_date_format).date()
            except ValueError:
                str_error = ('Date Parameter: {} value: {} is not valid for date format: {}'.format(self.label,value, date_format))
                return str_error
        self.value = date_value
        # self.date_format = str_date_format
        return str_error

    def __str__(self):
        str_value = 'None'
        if self.value:
            str_value = self.value.strftime(self.date_format)
        return str(eval(self.output_format.format(str_value)))

    def __unicode__(self):
        str_value = 'None'
        if self.value:
            str_value = self.value.strftime(self.date_format)
        return str(eval(self.output_format.format(str_value)))

    def __repr__(self):
        str_value = 'None'
        if self.value:
            str_value = self.value.strftime(self.date_format)
        return str(eval(self.output_format.format(str_value)))


class FileParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value, file_mode, domain = None):
        str_error = ''
        if value is None:
            str_error = ('File Parameter value is None')
            return str_error
        str_file_mode = file_mode
        if not isinstance(file_mode, str):
            try:
                str_file_mode = str(file_mode)
            except ValueError:
                str_error = ('File Parameter: {} file mode must be a string and is: {}'
                             .format(self.label, str(type(file_mode))))
                return str_error
        if (str_file_mode.casefold() != defs_pars.FILE_MODE_READ.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_WRITE.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_APPEND.casefold()):
            str_error = ('File Parameter: {} invalid file mode value: {}'
                         .format(self.label, str(type(file_mode))))
            return str_error
        if domain:
            if not isinstance(domain, list):
                str_error = ('File Parameter: {} domain must be a list and is: {}'.format(self.label, str(type(domain))))
                return str_error
            domain.sort()
        string_value = None
        if not isinstance(value, str):
            try:
                string_value = str(value)
            except ValueError:
                str_error = ('File Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                return str_error
        else:
            string_value = value
        file_path = ''
        if string_value: # maybe is empty
            file_path = os.path.normcase(string_value)
            if domain:
                file_extension = pathlib.Path(file_path).suffix
                valid_value = False
                for domain_value in domain:
                    if domain_value.casefold() == file_extension.casefold():
                        valid_value = True
                        break
                if not valid_value:
                    str_value = eval(self.output_format.format(string_value))
                    str_error = (
                        'File Parameter: {} value: {} is not in domain values: {}'
                        .format(self.label, str_value, domain))
                    return str_error
            if (str_file_mode.casefold() == defs_pars.FILE_MODE_READ.casefold()
                    or str_file_mode.casefold() == defs_pars.FILE_MODE_APPEND.casefold()):
                if not os.path.isfile(file_path):
                    # str_error = ('File Parameter: {} not exists file for read/append:\n{}'
                    #              .format(self.label, file_path))
                    # return str_error
                    is_error = None
            else:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    if os.path.isfile(file_path):
                        str_error = ('File Parameter: {} error removing existing file for write:\n{}'
                                     .format(self.label, file_path))
                        return str_error
        self.value = file_path
        self.file_mode = str_file_mode.casefold()
        if domain:
            self.domain = domain
        return str_error

    def set_input(self, value):
        str_error = ''
        if not isinstance(value, bool):
            str_error = ('File Parameter: {} input must be a boolean and is: {}'.format(self.label, str(type(value))))
            return str_error
        self.value = value
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('File Parameter value is None')
            return str_error
        if not isinstance(value, str):
            str_value = None
            try:
                str_value = str(value)
            except ValueError:
                str_error = (
                    'File Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                return str_error
            value = str_value
        self.value = value
        return str_error


class IntegerParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)
        self.domain = None

    def get_value(self):
        return self.value

    def initialize(self, value, domain):
        str_error = ''
        if value is None:
            str_error = ('Integer Parameter value is None')
            return str_error
        if domain is None:
            str_error = ('Integer Parameter domain is None')
            return str_error
        if not isinstance(domain, list):
            str_error = ('Integer Parameter: {} domain must be a list and is: {}'.
                         format(self.label, str(type(domain))))
            return str_error
        if len(domain) < 2:
            str_error = ('Integer Parameter: {} domain must be a list with at least two values'.
                         format(self.label))
            return str_error
        int_domain = []
        for i in range(len(domain)):
            int_value = None
            try:
                int_value = int(domain[i])
            except ValueError:
                str_error = (
                    'Integer Parameter: {} domain value: {} must be a integer number and is: {}'.
                    format(self.label, str(i+1), str(type(domain[i]))))
                return str_error
            int_domain.append(int_value)
        int_domain.sort()
        int_value = None
        try:
            int_value = int(value)
        except ValueError:
            str_error = ('Integer Parameter: {} value must be a integer number and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        if len(int_domain) == 2:
            if int_value < int_domain[0] or int_value > int_domain[1]:
                str_value = eval(self.output_format.format(int_value))
                str_min_value = eval(self.output_format.format(int_domain[0]))
                str_max_value = eval(self.output_format.format(int_domain[1]))
                str_error = (
                    'Integer Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            if not int_value in int_domain:
                str_value = eval(self.output_format.format(int_value))
                str_error = (
                    'Integer Parameter: {} value: {} is not in domain values: {}'
                    .format(self.label, str_value, int_domain))
                return str_error
        self.value = int_value
        self.domain = int_domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Integer Parameter value is None')
            return str_error
        int_value = None
        try:
            int_value = int(value)
        except ValueError:
            str_error = ('Integer Parameter: {} value must be a integer and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        value = int_value
        if len(self.domain) == 2:
            if value < self.domain[0] or value > self.domain[1]:
                str_value = eval(self.output_format.format(value))
                str_min_value = eval(self.output_format.format(self.domain[0]))
                str_max_value = eval(self.output_format.format(self.domain[1]))
                str_error = (
                    'Integer Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            if not value in self.domain:
                str_value = eval(self.output_format.format(value))
                str_error = (
                    'Integer Parameter: {} value: {} is not in domain values: {}'
                    .format(self.label, str_value, self.domain))
                return str_error
        self.value = value
        return str_error


class PathParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self):
        str_error = ''
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Real Parameter value is None')
            return str_error
        if not isinstance(value, str):
            str_error = ('Path Parameter: {} value must be a string and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        self.value = value
        return str_error


class RealParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)
        self.domain = None
        self.tol = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE

    def get_value(self):
        return self.value

    def initialize(self, value, domain, tol=1e-9):
        str_error = ''
        if value is None:
            str_error = ('Real Parameter value is None')
            return str_error
        if domain is None:
            str_error = ('Real Parameter domain is None')
            return str_error
        if not isinstance(domain, list):
            str_error = ('Real Parameter: {} domain must be a list and is: {}'.
                         format(self.label, str(type(domain))))
            return str_error
        if len(domain) < 2:
            str_error = ('Real Parameter: {} domain must be a list with at least two values'.
                         format(self.label))
            return str_error
        float_domain = []
        for i in range(len(domain)):
            float_value = None
            try:
                float_value = float(domain[i])
            except ValueError:
                str_error = (
                    'Real Parameter: {} domain value: {} must be a real number and is: {}'.
                    format(self.label, str(i+1), str(type(domain[i]))))
                return str_error
            float_domain.append(float_value)
        float_domain.sort()
        float_value = None
        try:
            float_value = float(value)
        except ValueError:
            str_error = ('Real Parameter: {} value must be a real number and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        if len(float_domain) == 2:
            if float_value < float_domain[0] or float_value > float_domain[1]:
                str_value = eval(self.output_format.format(float_value))
                str_min_value = eval(self.output_format.format(float_domain[0]))
                str_max_value = eval(self.output_format.format(float_domain[1]))
                str_error = (
                    'Real Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            valid_value = False
            for i in range(len(float_domain)):
                if math.isclose(float_value, float_domain[i], rel_tol = tol):
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(float_value))
                str_error = (
                    'Real Parameter: {} value: {} is different from domain values'
                    .format(self.label, str_value))
                return str_error
        self.tol = tol
        self.value = float_value
        self.domain = float_domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Real Parameter value is None')
            return str_error
        float_value = None
        try:
            float_value = float(value)
        except ValueError:
            str_error = ('Real Parameter: {} value must be a real number and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        value = float_value
        if len(self.domain) == 2:
            if float_value < self.domain[0] or float_value > self.domain[1]:
                str_value = eval(self.output_format.format(float_value))
                str_min_value = eval(self.output_format.format(self.domain[0]))
                str_max_value = eval(self.output_format.format(self.domain[1]))
                str_error = (
                    'Real Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            valid_value = False
            for i in range(len(self.domain)):
                if math.isclose(float_value, self.domain[i], rel_tol = self.tol):
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(float_value))
                str_error = (
                    'Real Parameter: {} value: {} is different from domain values'
                    .format(self.label, str_value))
                return str_error
        self.value = value
        return str_error

    def __str__(self):
        str_value = str(eval(self.output_format.format(self.value)))
        # str_value = "None"
        # if self.value:
        #     if not isinstance(self.value, str):
        #         str_value = str(eval(self.output_format.format(self.value)))
        #     else:
        #         str_value = self.value
        return str_value

    def __unicode__(self):
        str_value = str(eval(self.output_format.format(self.value)))
        # str_value = "None"
        # if self.value:
        #     if not isinstance(self.value, str):
        #         str_value = str(eval(self.output_format.format(self.value)))
        #     else:
        #         str_value = self.value
        return str_value

    def __repr__(self):
        str_value = str(eval(self.output_format.format(self.value)))
        # str_value = "None"
        # if self.value:
        #     if not isinstance(self.value, str):
        #         str_value = str(eval(self.output_format.format(self.value)))
        #     else:
        #         str_value = self.value
        return str_value


class StringParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)
        self.domain = None

    def get_value(self):
        return self.value

    def initialize(self, value, domain = None):
        str_error = ''
        if value is None:
            str_error = ('String Parameter value is None')
            return str_error
        if domain:
            if not isinstance(domain, list):
                str_error = ('String Parameter: {} domain must be a list and is: {}'.format(self.label, str(type(domain))))
                return str_error
            domain.sort()
        string_value = None
        if not isinstance(value, str):
            try:
                string_value = str(value)
            except ValueError:
                str_error = ('String Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                return str_error
        else:
            string_value = value
        if domain:
            valid_value = False
            for domain_value in domain:
                if domain_value.casefold() == string_value.casefold():
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(string_value))
                str_error = (
                    'String Parameter: {} value: {} is not in domain values: {}'
                    .format(self.label, str_value, domain))
                return str_error
        self.value = string_value
        if domain:
            self.domain = domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('String Parameter value is None')
            return str_error
        if not isinstance(value, str):
            str_value = None
            try:
                str_value = str(value)
            except ValueError:
                str_error = (
                    'String Parameter: {} value must be a string and is: {}'.format(self.label, str(type(value))))
                return str_error
            value = str_value
        if self.domain:
            valid_value = False
            for domain_value in self.domain:
                if domain_value.casefold() == value.casefold():
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(value))
                str_error = (
                    'String Parameter: {} value: {} is not in domain values: {}'
                    .format(self.label, str_value, self.domain))
                return str_error
        self.value = value
        return str_error

class PhysicalQuantityParameter(RealParameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)
        self.domain = None
        self.tol = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE
        self.quantity = defs_pars.ureg.Quantity
        self.ui_unit = None
        self.computation_unit = None
        self.output_format_unit = None
        self.compatible_units = None

    def get_compatible_units(self):
        compatible_units = []
        for compatible_unit in self.compatible_units:
            if not compatible_unit in self.ignored_units:
                compatible_units.append(str(compatible_unit))
        return compatible_units

    def get_str_value_wihtout_unit(self):
        str_value = 'None'
        if self.quantity == None:
            return str_value
        computation_unit = self.quantity
        ui_unit = computation_unit.to(self.ui_unit)
        str_value = str(eval(self.output_format.format(ui_unit.magnitude)))
        if self.output_format_unit:
            str_unit = self.output_format_unit.format(ui_unit.units)
            # str_value += " " + str_unit
        return str_value

    def get_value(self, unit = '', to_ui_unit = True ):
        if not unit:
            if to_ui_unit:
                unit = self.ui_unit
            else:
                unit = self.computation_unit
        quantity_unit = None
        try:
            quantity_unit = self.quantity.to(unit)
        except Exception as quantity_error:
            str_error = (
                'Physical Quantity Parameter: {} converting to unit error:\n{}'.
                format(self.label, quantity_error))
            return str_error
        value = quantity_unit.magnitude
        return value

    def initialize(self, value, domain,
                   ui_unit, computation_unit, output_format_unit,
                   ignored_units,
                   valid_units,
                   tol = 1e-9):
        str_error = ''
        if value is None:
            str_error = ('Physical Quantity Parameter value is None')
            return str_error
        if not isinstance(ignored_units, list):
            str_error = ('Physical Quantity Parameter: {} ignored units must be a list and is: {}'.
                         format(self.label, str(type(ignored_units))))
            return str_error
        if not isinstance(valid_units, list):
            str_error = ('Physical Quantity Parameter: {} valid units must be a list and is: {}'.
                         format(self.label, str(type(valid_units))))
            return str_error
        if domain is None:
            str_error = ('Physical Quantity Parameter domain is None')
            return str_error
        if not isinstance(domain, list):
            str_error = ('Physical Quantity Parameter: {} domain must be a list and is: {}'.
                         format(self.label, str(type(domain))))
            return str_error
        if len(domain) < 2:
            str_error = ('Physical Quantity Parameter: {} domain must be a list with at least two values'.
                         format(self.label))
            return str_error
        float_domain = []
        for i in range(len(domain)):
            float_value = None
            try:
                float_value = float(domain[i])
            except ValueError:
                str_error = (
                    'Physical Quantity Parameter: {} domain value: {} must be a real number and is: {}'.
                    format(self.label, str(i+1), str(type(domain[i]))))
                return str_error
            float_domain.append(float_value)
        float_domain.sort()
        float_value = None
        try:
            float_value = float(value)
        except ValueError:
            str_error = ('Physical Quantity Parameter: {} value must be a real number and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        if len(float_domain) == 2:
            if float_value < float_domain[0] or float_value > float_domain[1]:
                str_value = eval(self.output_format.format(float_value))
                str_min_value = eval(self.output_format.format(float_domain[0]))
                str_max_value = eval(self.output_format.format(float_domain[1]))
                str_error = (
                    'Physical Quantity Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            valid_value = False
            for i in range(len(float_domain)):
                if math.isclose(float_value, float_domain[i], rel_tol = tol):
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(float_value))
                str_error = (
                    'Physical Quantity Parameter: {} value: {} is different from domain values'
                    .format(self.label, str_value))
                return str_error
        if ui_unit is None:
            str_error = ('Physical Quantity Parameter ui unit is None')
            return str_error
        if not isinstance(ui_unit, str):
            str_error = (
                    'Physical Quantity Parameter: {} ui unit must be a string and is: {}'.
                    format(self.label, str(type(ui_unit))))
            return str_error
        if len(valid_units) > 0:
            if not ui_unit in valid_units:
                str_error = (
                    'Physical Quantity Parameter: {} ui unit: {} is not a valid unit'.format(self.label, ui_unit))
                return str_error
        quantity_ui_unit = defs_pars.ureg.Quantity
        try:
            quantity_ui_unit = quantity_ui_unit(float_value, ui_unit)
        except Exception as quantity_error:
            str_error = (
                    'Physical Quantity Parameter: {} initializing error:\n{}'.
                    format(self.label, quantity_error))
            return str_error
        if computation_unit is None:
            str_error = ('Physical Quantity Parameter computation unit is None')
            return str_error
        if len(valid_units) > 0:
            if not computation_unit in valid_units:
                str_error = (
                    'Physical Quantity Parameter: {} computation unit: {} is not a valid unit'.
                    format(self.label, computation_unit))
                return str_error
        if not isinstance(computation_unit, str):
            str_error = (
                    'Physical Quantity Parameter: {} computation unit must be a string and is: {}'.
                    format(self.label, str(type(computation_unit))))
            return str_error
        quantity_computation_unit = None
        try:
            quantity_computation_unit = quantity_ui_unit.to(computation_unit)
        except Exception as quantity_error:
            str_error = (
                    'Physical Quantity Parameter: {} converting to computation unit error:\n{}'.
                    format(self.label, quantity_error))
            return str_error
        compatible_units = defs_pars.ureg.get_compatible_units(quantity_ui_unit.dimensionality)
        if len(compatible_units) == 0:
            compatible_units = []
            str_dimensionality = str(quantity_ui_unit.dimensionality)
            values = [k for k, v in defs_pars.ureg._cache.dimensionality.items() if
                      v == UnitsContainer({str_dimensionality: 1})]
            for i in range(len(values)):
                for key in values[i]._d:
                    if key != str_dimensionality:
                        compatible_units.append(key)
        if output_format_unit is None:
            str_error = ('Physical Quantity Parameter output format unit is None')
            return str_error
        if not isinstance(output_format_unit, str):
            str_error = (
                    'Physical Quantity Parameter: {} output format unit must be a string and is: {}'.
                    format(self.label, str(type(output_format_unit))))
            return str_error
        self.tol = tol
        self.quantity = quantity_computation_unit
        self.domain = float_domain
        self.ui_unit = ui_unit
        self.computation_unit = computation_unit
        self.output_format_unit = output_format_unit
        self.compatible_units = compatible_units
        self.ignored_units = ignored_units
        self.valid_units = valid_units
        return str_error

    def set_value(self, value, unit = '', from_ui_unit = True ):
        str_error = ''
        if value is None:
            str_error = ('Physical Quantity Parameter value is None')
            return str_error
        float_value = None
        try:
            float_value = float(value)
        except ValueError:
            str_error = ('Physical Quantity Parameter: {} value must be a real number and is: {}'.
                         format(self.label, str(type(value))))
            return str_error
        value = float_value
        if not unit:
            if from_ui_unit:
                unit = self.ui_unit
            else:
                unit = self.computation_unit
        quantity_unit = defs_pars.ureg.Quantity
        try:
            quantity_unit = quantity_unit(float_value, unit)
        except Exception as quantity_error:
            str_error = (
                    'Physical Quantity Parameter: {} setting value error:\n{}'.
                    format(self.label, quantity_error))
            return str_error
        quantity_ui_unit = quantity_unit
        if unit != self.ui_unit:
            try:
                quantity_ui_unit = quantity_unit.to(self.ui_unit)
            except Exception as quantity_error:
                str_error = (
                    'Physical Quantity Parameter: {} converting to ui unit error:\n{}'.
                    format(self.label, quantity_error))
                return str_error
        float_value = float(quantity_ui_unit.magnitude)
        if len(self.domain) == 2:
            if float_value < self.domain[0] or float_value > self.domain[1]:
                str_value = eval(self.output_format.format(float_value))
                str_min_value = eval(self.output_format.format(self.domain[0]))
                str_max_value = eval(self.output_format.format(self.domain[1]))
                str_error = (
                    'Physical Quantity Parameter: {} value: {} is out of domain: [{}, {}]'
                    .format(self.label, str_value, str_min_value, str_max_value))
                return str_error
        else:
            valid_value = False
            for i in range(len(self.domain)):
                if math.isclose(float_value, self.domain[i], rel_tol = self.tol):
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(float_value))
                str_error = (
                    'Physical Quantity Parameter: {} value: {} is different from domain values'
                    .format(self.label, str_value))
                return str_error
        quantity_computation_unit = quantity_unit
        if unit != self.computation_unit:
            try:
                quantity_computation_unit = quantity_unit.to(self.computation_unit)
            except Exception as quantity_error:
                str_error = (
                    'Physical Quantity Parameter: {} converting to computation unit error:\n{}'.
                    format(self.label, quantity_error))
                return str_error
        self.quantity = quantity_computation_unit
        return str_error

    def __str__(self):
        str_value = 'None'
        if self.quantity == None:
            return str_value
        computation_unit = self.quantity
        ui_unit = computation_unit.to(self.ui_unit)
        str_value = str(eval(self.output_format.format(ui_unit.magnitude)))
        if self.output_format_unit:
            str_unit = self.output_format_unit.format(ui_unit.units)
            str_value += " " + str_unit
        return str_value

    def __unicode__(self):
        str_value = 'None'
        if self.quantity == None:
            return str_value
        computation_unit = self.quantity
        ui_unit = computation_unit.to(self.ui_unit)
        str_value = str(eval(self.output_format.format(ui_unit.magnitude)))
        if self.output_format_unit:
            str_unit = self.output_format_unit.format(ui_unit.units)
            str_value += " " + str_unit
        return str_value

    def __repr__(self):
        str_value = 'None'
        if self.quantity == None:
            return str_value
        computation_unit = self.quantity
        ui_unit = computation_unit.to(self.ui_unit)
        str_value = str(eval(self.output_format.format(ui_unit.magnitude)))
        if self.output_format_unit:
            str_unit = self.output_format_unit.format(ui_unit.units)
            str_value += " " + str_unit
        return str_value


class RasterLayerParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value, file_mode, domain = None):
        str_error = ''
        if value is None:
            str_error = ('Raster Layer Parameter value is None')
            return str_error
        str_file_mode = file_mode
        if not isinstance(file_mode, str):
            try:
                str_file_mode = str(file_mode)
            except ValueError:
                str_error = ('Raster Layer Parameter: {} file mode must be a string and is: {}'
                             .format(self.label, str(type(file_mode))))
                return str_error
        if (str_file_mode.casefold() != defs_pars.FILE_MODE_READ.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_WRITE.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_APPEND.casefold()):
            str_error = ('File Parameter: {} invalid file mode value: {}'
                         .format(self.label, str(type(file_mode))))
            return str_error
        if domain:
            if not isinstance(domain, list):
                str_error = ('Vector Layer Parameter: {} domain must be a list and is: {}'
                             .format(self.label, str(type(domain))))
                return str_error
            domain.sort()
        if not isinstance(value, dict):
            str_error = ('Raster Layer Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_INDEX in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_INDEX))
            return str_error
        if not defs_pars.TAG_SCALE in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_SCALE))
            return str_error
        if not defs_pars.TAG_OFFSET in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_OFFSET))
            return str_error
        file_path = value[defs_pars.TAG_FILE_PATH].strip()
        if file_path: # maybe is empty
            file_path = os.path.normcase(file_path)
            if domain:
                file_extension = pathlib.Path(file_path).suffix
                valid_value = False
                for domain_value in domain:
                    if domain_value.casefold() == file_extension.casefold():
                        valid_value = True
                        break
                if not valid_value:
                    str_error = (
                        'Raster Layer Parameter: {} file:\n{}\nis not in domain values: {}'
                        .format(self.label, file_path, domain))
                    return str_error
            if (str_file_mode.casefold() == defs_pars.FILE_MODE_READ.casefold()
                    or str_file_mode.casefold() == defs_pars.FILE_MODE_APPEND.casefold()):
                if not os.path.isfile(file_path):
                    # str_error = ('Raster Layer Parameter: {} not exists file for read/append:\n{}'
                    #              .format(self.label, file_path))
                    # return str_error
                    is_error = None
            else:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    if os.path.isfile(file_path):
                        str_error = ('Raster Layer Parameter: {} error removing existing file for write:\n{}'
                                     .format(self.label, file_path))
                        return str_error
        self.value = value
        self.file_mode = str_file_mode.casefold()
        if domain:
            self.domain = domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Raster Layer Parameter value is None')
            return str_error
        if not isinstance(value, dict):
            str_error = ('Raster Layer Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_INDEX in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_INDEX))
            return str_error
        if not defs_pars.TAG_SCALE in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_SCALE))
            return str_error
        if not defs_pars.TAG_OFFSET in value:
            str_error = ('Raster Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_OFFSET))
            return str_error
        self.value = value
        return str_error


class VectorLayerParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value, file_mode, domain = None):
        str_error = ''
        if value is None:
            str_error = ('Vector Layer Parameter value is None')
            return str_error
        str_file_mode = file_mode
        if not isinstance(file_mode, str):
            try:
                str_file_mode = str(file_mode)
            except ValueError:
                str_error = ('Vector Layer Parameter: {} file mode must be a string and is: {}'
                             .format(self.label, str(type(file_mode))))
                return str_error
        if (str_file_mode.casefold() != defs_pars.FILE_MODE_READ.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_WRITE.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_APPEND.casefold()):
            str_error = ('File Parameter: {} invalid file mode value: {}'
                         .format(self.label, str(type(file_mode))))
            return str_error
        if domain:
            if not isinstance(domain, list):
                str_error = ('Vector Layer Parameter: {} domain must be a list and is: {}'
                             .format(self.label, str(type(domain))))
                return str_error
            domain.sort()
        if not isinstance(value, dict):
            str_error = ('Vector Layer Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_NAME in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_NAME))
            return str_error
        if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
            return str_error
        file_path = value[defs_pars.TAG_FILE_PATH].strip()
        layer_name = value[defs_pars.TAG_LAYER_NAME].strip()
        if file_path: # maybe is empty
            file_path = os.path.normcase(file_path)
            if domain:
                file_extension = pathlib.Path(file_path).suffix
                valid_value = False
                for domain_value in domain:
                    if domain_value.casefold() == file_extension.casefold():
                        valid_value = True
                        break
                if not valid_value:
                    str_error = (
                        'Vector Layer Parameter: {} file:\n{}\nis not in domain values: {}'
                        .format(self.label, file_path, domain))
                    return str_error
            if (str_file_mode.casefold() == defs_pars.FILE_MODE_READ.casefold()
                    or str_file_mode.casefold() == defs_pars.FILE_MODE_APPEND.casefold()):
                if not os.path.isfile(file_path):
                    # str_error = ('Vector Layer Parameter: {} not exists file for read/append:\n{}'
                    #              .format(self.label, file_path))
                    # return str_error
                    is_error = None
            else:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    if os.path.isfile(file_path):
                        str_error = ('Vector Layer Parameter: {} error removing existing file for write:\n{}'
                                     .format(self.label, file_path))
                        return str_error
        self.value = value
        self.file_mode = str_file_mode.casefold()
        if domain:
            self.domain = domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Vector Layer Parameter value is None')
            return str_error
        if not isinstance(value, dict):
            str_error = ('Vector Layer Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_NAME in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_NAME))
            return str_error
        if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
            str_error = ('Vector Layer Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
            return str_error
        self.value = value
        return str_error


class VectorLayerFieldNameParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory, output, enabled = True):
        super().__init__(label, description, output_format, mandatory, output, enabled)

    def get_value(self):
        return self.value

    def initialize(self, value, file_mode, domain = None):
        str_error = ''
        if value is None:
            str_error = ('Vector Layer Field Name Parameter value is None')
            return str_error
        str_file_mode = file_mode
        if not isinstance(file_mode, str):
            try:
                str_file_mode = str(file_mode)
            except ValueError:
                str_error = ('Vector Layer Field Name Parameter: {} file mode must be a string and is: {}'
                             .format(self.label, str(type(file_mode))))
                return str_error
        if (str_file_mode.casefold() != defs_pars.FILE_MODE_READ.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_WRITE.casefold()
                and str_file_mode.casefold() != defs_pars.FILE_MODE_APPEND.casefold()):
            str_error = ('File Parameter: {} invalid file mode value: {}'
                         .format(self.label, str(type(file_mode))))
            return str_error
        if domain:
            if not isinstance(domain, list):
                str_error = ('Vector Layer Field Name Parameter: {} domain must be a list and is: {}'
                             .format(self.label, str(type(domain))))
                return str_error
            domain.sort()
        if not isinstance(value, dict):
            str_error = ('Vector Layer Field Name Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_NAME))
            return str_error
        if not defs_pars.TAG_FIELD_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FIELD_NAME))
            return str_error
        if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
            return str_error
        file_path = value[defs_pars.TAG_FILE_PATH].strip()
        layer_name = value[defs_pars.TAG_LAYER_NAME].strip()
        field_name = value[defs_pars.TAG_FIELD_NAME].strip()
        if file_path: # maybe is empty
            file_path = os.path.normcase(file_path)
            if domain:
                file_extension = pathlib.Path(file_path).suffix
                valid_value = False
                for domain_value in domain:
                    if domain_value.casefold() == file_extension.casefold():
                        valid_value = True
                        break
                if not valid_value:
                    str_error = (
                        'Vector Layer Field Name Parameter: {} file:\n{}\nis not in domain values: {}'
                        .format(self.label, file_path, domain))
                    return str_error
            if (str_file_mode.casefold() == defs_pars.FILE_MODE_READ.casefold()
                    or str_file_mode.casefold() == defs_pars.FILE_MODE_APPEND.casefold()):
                if not os.path.isfile(file_path):
                    # str_error = ('Vector Layer Field Name Parameter: {} not exists file for read/append:\n{}'
                    #              .format(self.label, file_path))
                    # return str_error
                    is_error = None
            else:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    if os.path.isfile(file_path):
                        str_error = ('Vector Layer Field Name Parameter: {} error removing existing file for write:\n{}'
                                     .format(self.label, file_path))
                        return str_error
        self.value = value
        self.file_mode = str_file_mode.casefold()
        if domain:
            self.domain = domain
        return str_error

    def set_value(self, value):
        str_error = ''
        if value is None:
            str_error = ('Vector Layer Field Name Parameter value is None')
            return str_error
        if not isinstance(value, dict):
            str_error = ('Vector Layer Field Name Parameter: {} value must be a dictionary and is: {}'
                         .format(self.label, str(type(value))))
            return str_error
        if not defs_pars.TAG_FILE_PATH in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FILE_PATH))
            return str_error
        if not defs_pars.TAG_LAYER_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_NAME))
            return str_error
        if not defs_pars.TAG_LAYER_GEOMETRY_TYPE in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_LAYER_GEOMETRY_TYPE))
            return str_error
        if not defs_pars.TAG_FIELD_NAME in value:
            str_error = ('Vector Layer Field Name Parameter: {} value must contain {}'
                         .format(self.label, defs_pars.TAG_FIELD_NAME))
            return str_error
        self.value = value
        return str_error




