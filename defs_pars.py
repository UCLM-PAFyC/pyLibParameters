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
PARAMETER_FIELD_DATE_FORMAT = "date_format"
PARAMETER_FIELD_FILE_MODE = "file_mode"
REAL_RELATIVE_TOLERANCE_DEFAULT_VALUE = 1e-9
PARAMETER_FIELD_QUANTITY_UI_UNIT = "ui_unit"
PARAMETER_FIELD_QUANTITY_COMPUTATION_UNIT = "computation_unit"
PARAMETER_FIELD_QUANTITY_OUTPUT_FORMAT_UNIT = "output_format_unit"

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
PARAMETER_TYPE_FILE = 'file'
# PARAMETER_TYPE_FILE_READ = 'file_read'
# PARAMETER_TYPE_FILE_WRITE = 'file_write'
# PARAMETER_TYPE_FILE_APPEND = 'file_append'
PARAMETER_TYPE_FILE_MODE = 'file_mode'
PARAMETER_TYPE_PHYSICAL_QUANTITY = 'physical_quantity'

FILE_MODE_READ = "read"
FILE_MODE_WRITE = "write"
FILE_MODE_APPEND = "append"

# types_group = {}
# types_group[PARAMETER_TYPE_FILE] = []
# types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_READ)
# types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_WRITE)
# types_group[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_APPEND)
# type_group_by_type = {}
# type_group_by_type[PARAMETER_TYPE_FILE_READ] = PARAMETER_TYPE_FILE
# type_group_by_type[PARAMETER_TYPE_FILE_WRITE] = PARAMETER_TYPE_FILE
# type_group_by_type[PARAMETER_TYPE_FILE_APPEND] = PARAMETER_TYPE_FILE

parameter_fields_by_type = {}
parameter_fields_by_type[PARAMETER_TYPE_REAL] = []
parameter_fields_by_type[PARAMETER_TYPE_REAL].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_INTEGER] = []
parameter_fields_by_type[PARAMETER_TYPE_INTEGER].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_DATE] = []
parameter_fields_by_type[PARAMETER_TYPE_DATE].append(PARAMETER_FIELD_DATE_FORMAT)
parameter_fields_by_type[PARAMETER_TYPE_STRING] = []
parameter_fields_by_type[PARAMETER_TYPE_BOOLEAN] = []
# parameter_fields_by_type[PARAMETER_TYPE_OPEN_FILE_TAG] = []
# parameter_fields_by_type[PARAMETER_TYPE_SAVE_FILE_TAG] = []
parameter_fields_by_type[PARAMETER_TYPE_FILE] = []
parameter_fields_by_type[PARAMETER_TYPE_FILE].append(PARAMETER_TYPE_FILE_MODE)
parameter_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY] = []
parameter_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY].append(PARAMETER_FIELD_DOMAIN)
parameter_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY].append(PARAMETER_FIELD_QUANTITY_UI_UNIT)
parameter_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY].append(PARAMETER_FIELD_QUANTITY_COMPUTATION_UNIT)
parameter_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY].append(PARAMETER_FIELD_QUANTITY_OUTPUT_FORMAT_UNIT)

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
parameter_optional_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY] = []
parameter_optional_fields_by_type[PARAMETER_TYPE_PHYSICAL_QUANTITY].append(PARAMETER_FIELD_TOLERANCE)

PARAMETERS_MANAGER_DIALOG_TITLE = "Parameters Manager"
PARAMETER_FIELD_LABEL_TAG = "Label"
PARAMETER_FIELD_VALUE_TAG = "Value"
PARAMETER_FIELD_DESCRIPTION_TAG = "Description"
PARAMETER_FIELD_LABEL_TOOLTIP = "Label"
PARAMETER_FIELD_VALUE_TOOLTIP = "Value"
PARAMETER_FIELD_DESCRIPTION_TOOLTIP = "Description"
PARAMETER_FIELD_ARGPARSE_TAG = "argparse"
PARAMETER_FIELD_OUTPUT_FORMAT_TAG = "Output format"
parameters_manager_dialog_field_by_header_tag = {}
parameters_manager_dialog_header=[PARAMETER_FIELD_LABEL_TAG,
                                  PARAMETER_FIELD_VALUE_TAG,
                                  PARAMETER_FIELD_DESCRIPTION_TAG]
parameters_manager_dialog_field_by_header_tag = {}
parameters_manager_dialog_field_by_header_tag[PARAMETER_FIELD_LABEL_TAG] = PARAMETER_FIELD_LABEL
parameters_manager_dialog_field_by_header_tag[PARAMETER_FIELD_VALUE_TAG] = PARAMETER_FIELD_VALUE
parameters_manager_dialog_field_by_header_tag[PARAMETER_FIELD_DESCRIPTION_TAG] = PARAMETER_FIELD_DESCRIPTION
parameters_manager_dialog_tooltip_by_header_tag = {}
parameters_manager_dialog_tooltip_by_header_tag[PARAMETER_FIELD_LABEL_TAG] = PARAMETER_FIELD_LABEL_TOOLTIP
parameters_manager_dialog_tooltip_by_header_tag[PARAMETER_FIELD_VALUE_TAG] = PARAMETER_FIELD_VALUE_TOOLTIP
parameters_manager_dialog_tooltip_by_header_tag[PARAMETER_FIELD_DESCRIPTION_TAG] = PARAMETER_FIELD_DESCRIPTION_TOOLTIP
