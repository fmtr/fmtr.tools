import logging
import os

from fmtr.tools import environment_tools
from fmtr.tools.constants import Constants

if environment_tools.IS_DEV:
    STREAM_DEFAULT = ENVIRONMENT_DEFAULT = Constants.DEVELOPMENT
else:
    STREAM_DEFAULT = None
    ENVIRONMENT_DEFAULT = Constants.PRODUCTION

IS_DEBUG = environment_tools.get(Constants.FMTR_LOG_LEVEL_KEY, None, converter=str.upper) == 'DEBUG'
LEVEL_DEFAULT = logging.DEBUG if IS_DEBUG else logging.INFO


def get_logger(name, version=None, host=Constants.FMTR_OBS_HOST, key=None, org=Constants.ORG_NAME,
               stream=STREAM_DEFAULT, environment=ENVIRONMENT_DEFAULT, level=LEVEL_DEFAULT):
    """

    Get a pre-configured logfire logger, if dependency is present, otherwise default to native logger.

    """

    stream = stream or name

    try:
        import logfire
    except ImportError:
        logger = logging.getLogger(None)
        logger.setLevel(level)
        logger.warning(f'Logging dependencies not installed. Using native logger.')

        return logger

    logger = logfire

    if key is None:
        key = environment_tools.get(Constants.FMTR_OBS_API_KEY_KEY, default=None)

    if key:
        url = f"https://{host}/api/{org}/v1/traces"
        headers = f"Authorization=Basic {key},stream-name={stream}"

        os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = url
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = headers
        os.environ["OTEL_EXPORTER_OTLP_INSECURE"] = str(False).lower()

    if not version:
        from fmtr.tools import version_tools
        version = version_tools.read()

    # Rigmarole to translate native levels to logfire/otel ones.
    lev_num_otel = logfire._internal.constants.LOGGING_TO_OTEL_LEVEL_NUMBERS[level]
    lev_name_otel = logfire._internal.constants.NUMBER_TO_LEVEL[lev_num_otel]

    console_opts = logfire.ConsoleOptions(
        colors='always',
        min_log_level=lev_name_otel,
    )

    logfire.configure(
        service_name=name,
        service_version=version,
        environment=environment,
        send_to_logfire=False,
        console=console_opts
    )

    if key is None:
        msg = f'Observability dependencies installed, but "{Constants.FMTR_OBS_API_KEY_KEY}" not set. Cloud observability will be disabled.'
        logger.warning(msg)

    return logger


logger = get_logger(name=Constants.LIBRARY_NAME)

if __name__ == '__main__':
    logger.info('Hello World')
    logger.warning('test warning')
    logger.debug('Hello World')
    logger
