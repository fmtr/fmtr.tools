import shlex
from dotenv import load_dotenv

from fmtr.tools.ha_tools import constants
from fmtr.tools.logging_tools import logger
from fmtr.tools.string_tools import ELLIPSIS


def apply_addon_env():
    path = constants.PATH_ADDON_ENV
    if not path.exists():
        return

    logger.warning(f'Loading AddOn environment file from "{path}"...')
    load_dotenv(path)


def convert_options_env() -> str:
    """

    Convert Home Assistant AddOn options.json to a sourcable environment file.

    """
    path = constants.PATH_ADDON_OPTIONS
    data = path.read_json()

    lines = []

    with logger.span(f'Converting AddOn "{path}" to environment variables...'):
        for key, value in data.items():
            key_env = key.upper()
            val_env = shlex.quote(str(value))
            logger.debug(f'Converting {key_env}={ELLIPSIS}" to environment variable...')
            line = f'export {key_env}={val_env}'
            lines.append(line)

    text = '\n'.join(lines)
    return text
