import sys

from loguru import logger as logger_loguru

from fmtr.tools.config import ToolsConfig
from fmtr.tools.config_tools import ConfigClass
from fmtr.tools.environment_tools import get
from fmtr.tools.path_tools import Path


class LoggingConfig(ConfigClass):
    SEP = ' '
    TIME = '<bold><green>{time:' + ToolsConfig.DATETIME_FILENAME_FORMAT + '}</green></bold>'
    ICON = '<level>{level.icon}</level>'
    LEVEL = '<level>{level:<8}</level>'
    FILE = '{file}:{line}'
    FUNCTION = '{function}(…)'
    MESSAGE = '{message}'
    DEFAULT_LEVEL_KEY = 'FMTR_LOG_LEVEL'
    DEFAULT_LEVEL = get(DEFAULT_LEVEL_KEY, 'INFO')

    FILENAME = f'log-{ToolsConfig.DATETIME_NOW_STR}.log'


def default_filter(record):
    return True


def default_patch(record):
    return record


def get_logger(logger=logger_loguru, terminal=True, level=LoggingConfig.DEFAULT_LEVEL, time_format=LoggingConfig.TIME,
               icon_format=LoggingConfig.ICON,
               level_format=LoggingConfig.LEVEL, file_format=LoggingConfig.FILE, function_format=LoggingConfig.FUNCTION,
               message_format=LoggingConfig.MESSAGE,
               logfile=False, logfile_dir=None):
    """



    """
    components = [time_format, icon_format, level_format, file_format, function_format, message_format]
    format = LoggingConfig.SEP.join([component for component in components if component])
    logger.remove()

    if terminal:
        logger.add(sys.stderr, format=format, level=level, filter=default_filter)
        logger = logger.patch(default_patch)

    if logfile:
        logfile_dir = Path(logfile_dir or '.')
        logfile_path = logfile_dir / LoggingConfig.FILENAME
        logger.add(logfile_path, format=format)

    return logger


logger = get_logger()
