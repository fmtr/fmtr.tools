import datetime


class Constants:
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

    ARROW = '→'
    ARROW_SEP = f' {ARROW} '

    FMTR_DEV_KEY = 'FMTR_DEV'
    FMTR_LOG_LEVEL_KEY = 'FMTR_LOG_LEVEL'
    FMTR_OBS_API_KEY_KEY = 'FMTR_OBS_API_KEY'
    FMTR_OBS_HOST = 'obs.sv.fmtr.dev'

    FMTR_REMOTE_DEBUG_HOST_KEY = 'FMTR_DEBUG_HOST'
    FMTR_REMOTE_DEBUG_HOST_DEFAULT = 'ws.lan'
    FMTR_REMOTE_DEBUG_PORT_DEFAULT = 5679
    FMTR_REMOTE_DEBUG_ENABLED_KEY = 'FMTR_REMOTE_DEBUG_ENABLED'

    FMTR_OPENAI_API_KEY_KEY = 'FMTR_OPENAI_API_KEY'

    FMTR_AI_HOST_KEY = 'FMTR_URL_HOST'
    FMTR_AI_HOST_DEFAULT = 'ai.gex.fmtr.dev'

    FILENAME_CONFIG = 'settings.yaml'
    DIR_NAME_REPO = 'repo'
    DIR_NAME_DATA = 'data'
    DIR_NAME_CACHE = 'cache'
    DIR_NAME_ARTIFACT = 'artifact'
    DIR_NAME_SOURCE = 'source'
    FILENAME_VERSION = 'version'
    DIR_NAME_HF = 'hf'

    ENTRYPOINTS_DIR = 'entrypoints'
    PACKAGE_EXCLUDE_DIRS = {'data', 'build', 'dist', '.*', '*egg-info*'}
    INIT_FILENAME = '__init__.py'

    DEVELOPMENT = "development"
    PRODUCTION = "production"

    INFRA = 'infra'
