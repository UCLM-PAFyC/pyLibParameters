# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

PARAMETERS = "parameters"
PARAMETER_FIELD_LABEL = "label"
PARAMETER_FIELD_DESCRIPTION = "description"
PARAMETER_FIELD_TYPE = "type"
PARAMETER_FIELD_VALUE = "value"
PARAMETER_FIELD_OUTPUT_FORMAT = "output_format"
PARAMETER_FIELD_DOMAIN = "domain"
PARAMETER_FIELD_TOLERANCE = "tolerance"
PARAMETER_FIELD_ARGPARSER = "argparser"
REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE = 1e-9

parameter_common_fields = []
parameter_common_fields.append(PARAMETER_FIELD_LABEL)
parameter_common_fields.append(PARAMETER_FIELD_ARGPARSER)
parameter_common_fields.append(PARAMETER_FIELD_DESCRIPTION)
parameter_common_fields.append(PARAMETER_FIELD_TYPE)
parameter_common_fields.append(PARAMETER_FIELD_VALUE)
parameter_common_fields.append(PARAMETER_FIELD_OUTPUT_FORMAT)

PARAMETER_TYPE_REAL = 'real'
PARAMETER_TYPE_INTEGER = 'integer'
PARAMETER_TYPE_DATE = 'date'
PARAMETER_TYPE_STRING = 'string'
PARAMETER_TYPE_BOOLEAN = 'boolean'
PARAMETER_TYPE_FILE_READ = 'file_read'
PARAMETER_TYPE_FILE_WRITE = 'file_write'
PARAMETER_TYPE_FILE_APPEND = 'file_append'
PARAMETER_TYPE_FILE = 'file'

FILE_MODE_READ = "read"
FILE_MODE_WRITE = "write"
FILE_MODE_APPEND = "append"

types_group = {}
types_group[PARAMETER_TYPE_FILE] = []
types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_READ)
types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_WRITE)
types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_APPEND)
type_group_by_type = {}
type_group_by_type[PARAMETER_TYPE_FILE_READ] = PARAMETER_TYPE_FILE
type_group_by_type[PARAMETER_TYPE_FILE_WRITE] = PARAMETER_TYPE_FILE
type_group_by_type[PARAMETER_TYPE_FILE_APPEND] = PARAMETER_TYPE_FILE

parameter_fields_by_type = {}
parameter_fields_by_type[PARAMETER_TYPE_REAL] = []
parameter_fields_by_type[PARAMETER_TYPE_REAL].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_INTEGER] = []
parameter_fields_by_type[PARAMETER_TYPE_INTEGER].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_DATE] = []
parameter_fields_by_type[PARAMETER_TYPE_STRING] = []
parameter_fields_by_type[PARAMETER_TYPE_BOOLEAN] = []
# parameter_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG] = []
# parameter_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_FILE] = []

parameter_optional_fields_by_type = {}
parameter_optional_fields_by_type[PARAMETER_TYPE_REAL] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_REAL].append(PARAMETER_FIELD_TOLERANCE)
parameter_optional_fields_by_type[PARAMETER_TYPE_INTEGER] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_DATE] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_STRING] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_STRING].append(PARAMETER_FIELD_DOMAIN)
parameter_optional_fields_by_type[PARAMETER_TYPE_BOOLEAN] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG].append(PARAMETER_FIELD_DOMAIN)
# parameter_optional_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG] = []
# parameter_optional_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG].append(PARAMETER_FIELD_DOMAIN)
parameter_optional_fields_by_type[PARAMETER_TYPE_FILE] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_FILE].append(PARAMETER_FIELD_DOMAIN)

