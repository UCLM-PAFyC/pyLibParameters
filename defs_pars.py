# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

PARAMETERS_TAG = "parameters"
PARAMETER_FIELD_LABEL = "label"
PARAMETER_FIELD_DESCRIPTION = "description"
PARAMETER_FIELD_TYPE = "type"
PARAMETER_FIELD_VALUE = "value"
PARAMETER_FIELD_OUTPUT_FORMAT = "output_format"
PARAMETER_FIELD_DOMAIN = "domain"
PARAMETER_FIELD_TOLERANCE = "tolerance"
REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE = 1e-9

parameter_common_fields = []
parameter_common_fields.append(PARAMETER_FIELD_LABEL)
parameter_common_fields.append(PARAMETER_FIELD_DESCRIPTION)
parameter_common_fields.append(PARAMETER_FIELD_TYPE)
parameter_common_fields.append(PARAMETER_FIELD_VALUE)
parameter_common_fields.append(PARAMETER_FIELD_OUTPUT_FORMAT)

PARAMETER_TYPE_REAL_TAG = 'real'
PARAMETER_TYPE_INTEGER_TAG = 'integer'
PARAMETER_TYPE_DATE_TAG = 'date'
PARAMETER_TYPE_STRING_TAG = 'string'
PARAMETER_TYPE_BOOLEAN_TAG = 'boolean'
PARAMETER_TYPE_OPEN_FILE_TAG = 'open_file'
PARAMETER_TYPE_SAVE_FILE_TAG = 'save_file'
PARAMETER_TYPE_FILE_TAG = 'file' # open or save, only one

parameter_fields_by_type = {}
parameter_fields_by_type[PARAMETER_TYPE_REAL_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_REAL_TAG].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_INTEGER_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_INTEGER_TAG].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_DATE_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_STRING_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_BOOLEAN_TAG] = []
# parameter_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG] = []
# parameter_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_FILE_TAG] = []

parameter_optional_fields_by_type = {}
parameter_optional_fields_by_type[PARAMETER_TYPE_REAL_TAG] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_REAL_TAG].append(PARAMETER_FIELD_TOLERANCE)
parameter_optional_fields_by_type[PARAMETER_TYPE_INTEGER_TAG] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_DATE_TAG] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_STRING_TAG] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_STRING_TAG].append(PARAMETER_FIELD_DOMAIN)
parameter_optional_fields_by_type[PARAMETER_TYPE_BOOLEAN_TAG] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG].append(PARAMETER_FIELD_DOMAIN)
# parameter_optional_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG].append(PARAMETER_FIELD_DOMAIN)
parameter_optional_fields_by_type[PARAMETER_TYPE_FILE_TAG] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_FILE_TAG].append(PARAMETER_FIELD_DOMAIN)

