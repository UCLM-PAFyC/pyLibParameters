# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
import math
import defs_pars
import pathlib

class Parameter:
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        self.label = label
        self.description = description
        self.output_format = output_format
        self.value = None
        self.mandatory = mandatory
        self.enabled = enabled

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def __str__(self):
        str_value = "None"
        if self.value:
            if not isinstance(self.value, str):
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
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)

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


class FileParameter(Parameter):
    def __init__(self, label, description, output_format, file_open = True, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)
        self.file_open = file_open # else save

    def get_value(self):
        return self.value

    def initialize(self, value, domain = None):
        str_error = ''
        if value is None:
            str_error = ('File Parameter value is None')
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
        if self.file_open:
            if not os.path.isfile(file_path):
                str_error = ('File Parameter: {} not exists file for input:\n{}'.format(self.label, file_path))
                return str_error
        else:
            if os.path.isfile(file_path):
                str_error = ('File Parameter: {} exists file for output:\n{}'.format(self.label, file_path))
                return str_error
        self.value = file_path
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
            str_error = ('Real Parameter value is None')
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
        self.value = value
        return str_error


class IntegerParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)
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
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)

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
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)
        self.domain = None
        self.rel_tol = defs_pars.REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE

    def get_value(self):
        return self.value

    def initialize(self, value, domain, rel_tol=1e-9):
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
                if math.isclose(float_value, float_domain[i], rel_tol):
                    valid_value = True
                    break
            if not valid_value:
                str_value = eval(self.output_format.format(float_value))
                str_error = (
                    'Real Parameter: {} value: {} is different from domain values'
                    .format(self.label, str_value))
                return str_error
        self.rel_tol = rel_tol
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
                if math.isclose(float_value, self.domain[i], self.rel_tol):
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


class StringParameter(Parameter):
    def __init__(self, label, description, output_format, mandatory = True, enabled = True):
        super().__init__(label, description, output_format, mandatory, enabled)

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
            str_error = ('Real Parameter value is None')
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
