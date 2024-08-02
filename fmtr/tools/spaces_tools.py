import sys
from os import getenv

import importlib
import logging
import subprocess

from fmtr.tools import netrc_tools


def run():
    FMTR_LOG_LEVEL = getenv('FMTR_LOG_LEVEL', 'INFO')
    logging.getLogger().setLevel(FMTR_LOG_LEVEL)

    MODULE_NAME = getenv('PACKAGE_NAME')
    if not MODULE_NAME:
        raise KeyError('No MODULE_NAME set.')

    PIP_INDEX_URL = getenv('PIP_INDEX_URL')
    if not PIP_INDEX_URL:
        raise KeyError('No PIP_INDEX_URL set.')

    PIP_USERNAME = getenv('PIP_USERNAME')
    if not PIP_USERNAME:
        raise KeyError('No PIP_USERNAME set.')

    PIP_PASSWORD = getenv('PIP_PASSWORD')
    if not PIP_PASSWORD:
        raise KeyError('No PIP_PASSWORD set.')

    with netrc_tools.get() as netrc_obj:
        netrc_obj[PIP_INDEX_URL] = {
            netrc_tools.LOGIN: PIP_USERNAME,
            netrc_tools.PASSWORD: PIP_PASSWORD
        }

    print(f'Starting {MODULE_NAME}...')

    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', MODULE_NAME, '--no-input', '--index-url', f'https://{PIP_INDEX_URL}'],
        check=True
    )

    interface = importlib.import_module(f'{MODULE_NAME}.interface')
    interface.run()
