import logging
import os

from fmtr.tools import environment_tools
from fmtr.tools.constants import Constants

DEVELOPMENT = "development"
PRODUCTION = "production"
STREAM_DEFAULT = DEVELOPMENT
ENVIRONMENT_DEFAULT = DEVELOPMENT

LEVEL_DEFAULT = logging.DEBUG if environment_tools.IS_DEBUG else logging.INFO


def get_logger(name, version=None, host=Constants.FMTR_OBS_HOST, key=None, org=Constants.ORG_NAME,
               stream=STREAM_DEFAULT,
               environment=ENVIRONMENT_DEFAULT, level=LEVEL_DEFAULT):
    """

    Get a pre-configured logfire logger, if dependency is present, otherwise default to native logger.

    """

    try:
        import logfire
    except ImportError:
        logger = logging.getLogger(None)
        logger.setLevel(level)
        logger.warning(f'Logging dependencies not installed. Using native logger.')

        return logger

    if key is None:
        key = environment_tools.get(Constants.FMTR_OBS_API_KEY_KEY)
    url = f"https://{host}/api/{org}/v1/traces"
    headers = f"Authorization=Basic {key},stream-name={stream}"

    os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = url
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = headers
    os.environ["OTEL_EXPORTER_OTLP_INSECURE"] = str(False).lower()

    if not version:
        from fmtr.tools import version_tools
        version = version_tools.read()

    logfire.configure(
        service_name=name,
        service_version=version,
        environment=environment,
        send_to_logfire=False,
        console=logfire.ConsoleOptions(colors='always' if environment_tools.IS_DEBUG else 'auto')
    )

    logging.getLogger(name).setLevel(level)

    logger = logfire
    return logger


logger = get_logger(name=Constants.LIBRARY_NAME)

if __name__ == '__main__':
    logger.info('Hello World')
    logger.warning('test warning')
    logger.debug('Hello World')
