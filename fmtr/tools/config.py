import datetime

from fmtr.tools.config_tools import ConfigClass


class ToolsConfig(ConfigClass):
    ENCODING = 'UTF-8'
    ORG_NAME = 'fmtr'
    LIBRARY_NAME = f'{ORG_NAME}.tools'
    DATE_FILENAME_FORMAT = '%Y-%m-%d'
    TIME_FILENAME_FORMAT = '%H-%M-%S'

    DATETIME_SEMVER_BUILD_FORMAT = f'{DATE_FILENAME_FORMAT}-{TIME_FILENAME_FORMAT}'
    DATETIME_FILENAME_FORMAT = f'{DATE_FILENAME_FORMAT}@{TIME_FILENAME_FORMAT}'
    DATETIME_NOW = datetime.datetime.now(datetime.timezone.utc)
    DATETIME_NOW_STR = DATETIME_NOW.strftime(DATETIME_FILENAME_FORMAT)
    SERIALIZATION_INDENT = 4

    FMTR_LOG_LEVEL_KEY = 'FMTR_LOG_LEVEL'
    FMTR_OBS_API_KEY_KEY = 'FMTR_OBS_API_KEY'
    FMTR_OBS_HOST = 'obs.sv.fmtr.dev'
