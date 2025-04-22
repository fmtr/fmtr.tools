from datetime import datetime
from pathlib import Path
from setuptools import find_namespace_packages, setup, find_packages

import requirements

ORG, PACKAGE = 'fmtr', 'tools'
ORG_GITHUB = ORG
AUTHOR = 'Frontmatter'
AUTHOR_EMAIL = 'innovative.fowler@mask.pro.fmtr.dev'
DESCRIPTION = 'Collection of high-level tools to simplify everyday development tasks, with a focus on AI/ML'

PATH_BASE = Path(__file__).absolute().parent
IS_SINGLETON = (PATH_BASE / PACKAGE).exists()
VERSION = 'version'

if IS_SINGLETON:
    packages = find_packages()
    package_dir = None
    name = PACKAGE
    path_ver = PATH_BASE / name / VERSION
else:
    packages = find_namespace_packages()
    package_dir = {'': '.'}
    name = f'{ORG}.{PACKAGE}'
    path_ver = PATH_BASE / ORG / PACKAGE / VERSION

__version__ = path_ver.read_text().strip()

setup(
    name=name,
    version=__version__,
    url=f'https://github.com/{ORG_GITHUB}/{name}',
    author=AUTHOR,
    license=f'Copyright © {datetime.now().year} {AUTHOR}. All rights reserved.',
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=(PATH_BASE / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    packages=packages,
    package_dir=package_dir,
    package_data={
        name: [VERSION],
    },
    entry_points={
        'console_scripts': requirements.CONSOLE_SCRIPTS,
    },
    install_requires=requirements.INSTALL,
    extras_require=requirements.EXTRAS,
)