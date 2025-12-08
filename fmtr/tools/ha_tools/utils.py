from dotenv import load_dotenv

from fmtr.tools.ha_tools.constants import PATH_ADDON_ENV
from fmtr.tools.logging_tools import logger


def apply_addon_env():
    if not PATH_ADDON_ENV.exists():
        return

    logger.warning(f'Loading AddOn environment file from "{PATH_ADDON_ENV}"...')
    load_dotenv(PATH_ADDON_ENV)
