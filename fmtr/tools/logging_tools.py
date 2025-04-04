import logging
import os

from fmtr.tools import environment_tools

DEVELOPMENT = "development"
PRODUCTION = "production"
HOST_DEFAULT = "log.sv.fmtr.dev"
ORG_DEFAULT = "fmtr"
STREAM_DEFAULT = DEVELOPMENT
ENVIRONMENT_DEFAULT = DEVELOPMENT

LEVEL_DEFAULT = logging.DEBUG if environment_tools.IS_DEBUG else logging.INFO


def get_logger(name, version, host=HOST_DEFAULT, org=ORG_DEFAULT, stream=STREAM_DEFAULT,
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

    key = environment_tools.get("FMTR_OBS_API_KEY")
    traces_endpoint = f"https://{host}/api/{org}/v1/traces"
    headers = f"Authorization=Basic {key},stream-name={stream}"

    os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = traces_endpoint
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = headers
    os.environ["OTEL_EXPORTER_OTLP_INSECURE"] = str(False).lower()

    logfire.configure(
        service_name=name,
        service_version=version,
        environment=environment,
        send_to_logfire=False

    )

    logging.getLogger(name).setLevel(level)

    logger = logfire
    return logger


logger = get_logger(name='fmtr.tools', version='0.0.0')

logger = get_logger()
