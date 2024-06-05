from pathlib import Path

from setuptools import find_namespace_packages, setup, find_packages

import requirements

name_ns, name_base = 'fmtr', 'tools'
name = f'{name_ns}.{name_base}'
path_segment = f'{name_ns}/{name_base}'
path_base = Path(__file__).absolute().parent
path_ver = path_base / path_segment / 'version'
__version__ = path_ver.read_text().strip()

packages = find_packages(where=path_segment)
packages = [name] + [f'{name}.{nsp}' for nsp in packages]

setup(
    name=name,
    version=__version__,
    url=f'https://github.com/{name_ns}/{name}',
    license='Copyright © 2024 Frontmatter. All rights reserved.',
    author='Frontmatter',
    author_email='innovative.fowler@mask.pro.fmtr.dev',
    description='Frontmatter tools for AI projects',
    packages=find_namespace_packages(),
    package_dir={'': '.'},
    package_data={
        name: [f'version'],
    },
    install_requires=requirements.INSTALL,
    extras_require=requirements.EXTRAS,
)
