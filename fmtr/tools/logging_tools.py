import logging


def get_logger(name, version, level, environment):
    """

    Get a pre-configured loguru logger, if dependency is present, otherwise default to native logger.

    """

    try:
        import logfire
    except ImportError:
        logger = logging.getLogger(None)
        logger.setLevel(level)
        logger.warning(f'Logging dependencies not installed. Using native logger.')

        return logger

    logfire.configure(
        service_name=name,
        service_version=version,
        environment=environment,
        send_to_logfire=False

    )

    logging.getLogger(name).setLevel(level)

    return logfire


logger = get_logger(name='fmtr.tools', version='0.0.0', level=logging.DEBUG, environment='dev')

logger = get_logger()
