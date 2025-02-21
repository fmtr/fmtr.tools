from diskcache import Cache

from fmtr.tools import logger, Path


class Disk(Cache):
    """

    Disk cache with subclass stub

    """

    def __init__(self, directory=None, **settings):
        """

        Surface additional open/create logging

        """
        if directory and not Path(directory).exists():
            logger.warning(f'Cache does not exist. Will be created. "{directory=}"...')

        logger.info(f'Initializing Disk Cache at path "{directory=}"...')

        super().__init__(directory=str(directory), **settings)
