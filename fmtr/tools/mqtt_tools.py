import logging

import aiomqtt

from fmtr.tools.logging_tools import logger, get_current_level, get_native_level_from_otel

LOGGER = logging.getLogger("mqtt")
LOGGER.handlers.clear()
LOGGER.addHandler(logger.LogfireLoggingHandler())
LOGGER.propagate = False


class Client(aiomqtt.Client):
    """

    Client stub

    """

    LOGGER = LOGGER

    def __init__(self, *args, **kwargs):
        """

        Seems a little goofy to sync with logfire on every init, but unsure how to do it better.

        """
        self.set_log_level()
        super().__init__(*args, **kwargs)

    def set_log_level(self):
        """

        Sync log level with logfire, which might have changed since handler set.

        """
        level = get_current_level(logger)
        level_no = get_native_level_from_otel(level)
        self.LOGGER.setLevel(level_no)

class Will(aiomqtt.Will):
    """

    Will stub

    """
