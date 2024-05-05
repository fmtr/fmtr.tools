from datetime import datetime

from fmtr.tools.config_tools import ConfigClass


class ToolsConfig(ConfigClass):
    ENCODING = 'UTF-8'
    LIBRARY_NAME = 'fmtr.tools'
    DATE_FILENAME_FORMAT = '%Y-%m-%d'
    DATETIME_FILENAME_FORMAT = f'{DATE_FILENAME_FORMAT}@%H-%M-%S'
    DATETIME_NOW = datetime.utcnow()
    DATETIME_NOW_STR = DATETIME_NOW.strftime(DATETIME_FILENAME_FORMAT)
    SERIALIZATION_INDENT = 4
