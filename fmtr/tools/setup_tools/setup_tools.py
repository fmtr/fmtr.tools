import sys
from datetime import datetime
from fnmatch import fnmatch
from functools import cached_property
from itertools import chain
from typing import List, Dict, Any, Callable, Optional

from fmtr.tools.constants import Constants
from fmtr.tools.path_tools import Path
from fmtr.tools.path_tools.path_tools import FromCallerMixin


class SetupPaths(FromCallerMixin):
    """

    Canonical paths for a repo.

    """

    def __init__(self, path=None, org=Constants.ORG_NAME):
        """

        Use calling module path as default path, if not otherwise specified.

        """
        if not path:
            path = self.from_caller()

        self.org_name = org
        self.repo = Path(path)

    @property
    def readme(self) -> Path:
        """

        Path of the README file.

        """
        return self.repo / 'README.md'

    @property
    def version(self) -> Path:
        """

        Path of the version file

        """
        return self.path / Constants.FILENAME_VERSION

    @cached_property
    def path(self) -> Path:
        """

        Infer the package path. It should be the only non-excluded package in the repo/org Path.

        """

        if self.is_namespace:
            base = self.org
        else:
            base = self.repo

        packages = [
            dir for dir in base.iterdir()
            if (dir / Constants.INIT_FILENAME).is_file()
               and not any(fnmatch(dir.name, pattern) for pattern in Constants.PACKAGE_EXCLUDE_DIRS)
        ]

        if len(packages) != 1:
            dirs_str = ', '.join([str(dir) for dir in packages])
            msg = f'Expected exactly one package in {self.repo}, found {dirs_str}'
            raise ValueError(msg)

        package = next(iter(packages))
        return package

    @property
    def org(self) -> bool | Path:
        """

        Get the org path, i.e. the namespace parent directory.

        """
        if not self.org_name:
            return False
        org = self.repo / self.org_name
        if not org.is_dir():
            return False
        return org

    @property
    def entrypoint(self) -> Path:
        """

        Path of base entrypoint module.

        """
        return self.path / Constants.ENTRYPOINT_FILE

    @property
    def entrypoints(self) -> Path:
        """

        Path of entrypoints sub-package.

        """
        return self.path / Constants.ENTRYPOINTS_DIR

    @property
    def is_namespace(self) -> bool:
        return bool(self.org)

    @property
    def name(self) -> str:
        return self.path.stem


class Setup(FromCallerMixin):
    """

    Abstract canonical pacakge setup for setuptools.

    """
    AUTHOR = 'Frontmatter'
    AUTHOR_EMAIL = 'innovative.fowler@mask.pro.fmtr.dev'

    REQUIREMENTS_ARG = 'requirements'

    ENTRYPOINT_COMMAND_SEP = '-'
    ENTRYPOINT_FUNCTION_SEP = '_'
    ENTRYPOINT_FUNC_NAME = 'main'

    def __init__(self, dependencies, paths=None, org=Constants.ORG_NAME, client=None, do_setup=True, **kwargs):
        """

        First check if commandline arguments for requirements output exist. If so, print them and return early.
        Otherwise, continue generating data to pass to setuptools.

        """
        self.kwargs = kwargs

        if type(dependencies) is not Dependencies:
            dependencies = Dependencies(**dependencies)
        self.dependencies = dependencies

        requirements_extras = self.get_requirements_extras()

        if requirements_extras:
            self.print_requirements()
            return

        self.org = org

        if not paths:
            paths = SetupPaths(path=self.from_caller(), org=self.org)
        self.paths = paths

        self.client = client

        if do_setup:
            self.setup()

    def get_requirements_extras(self) -> Optional[List[str]]:
        """

        Get list of extras from command line arguments.

        """
        if self.REQUIREMENTS_ARG not in sys.argv:
            return None

        extras_str = sys.argv[-1]
        extras = extras_str.split(',')
        return extras

    def print_requirements(self):
        """

        Output flat list of requirements for specified extras

        """
        reqs = []
        reqs += self.dependencies.install

        for extra in sys.argv[-1].split(','):
            reqs += self.dependencies.extras[extra]
        reqs = '\n'.join(reqs)
        print(reqs)

    @property
    def console_scripts(self) -> List[str]:
        """

        Generate console scripts for the `entrypoint` module - and/or any modules in `entrypoints` sub-package.

        """

        if not self.paths.entrypoints.exists():
            paths_mods = []
        else:
            paths_mods = list(self.paths.entrypoints.iterdir())

        names_mods = [path.stem for path in paths_mods if path.is_file() and path.name != Constants.INIT_FILENAME]
        command_suffixes = [name_mod.replace(self.ENTRYPOINT_FUNCTION_SEP, self.ENTRYPOINT_COMMAND_SEP) for name_mod in names_mods]
        commands = [f'{self.name_command}-{command_suffix}' for command_suffix in command_suffixes]
        paths = [f'{self.name}.{Constants.ENTRYPOINTS_DIR}.{name_mod}:{self.ENTRYPOINT_FUNC_NAME}' for name_mod in names_mods]

        if self.paths.entrypoint.exists():
            commands.append(self.name_command)
            path = f'{self.name}.{self.paths.entrypoint.stem}:{self.ENTRYPOINT_FUNC_NAME}'
            paths.append(path)

        console_scripts = [f'{command} = {path}' for command, path in zip(commands, paths)]

        return console_scripts

    @cached_property
    def name_command(self) -> str:
        """

        Name as a command, e.g. `fmtr-tools`

        """
        return self.name.replace('.', self.ENTRYPOINT_COMMAND_SEP)

    @property
    def name(self) -> str:
        """

        Full library name

        """
        if self.paths.is_namespace:
            return f'{self.paths.org_name}.{self.paths.name}'
        return self.paths.name

    @property
    def author(self) -> str:
        """

        Create appropriate author string

        """
        if self.client:
            return f'{self.AUTHOR} on behalf of {self.client}'
        return self.AUTHOR

    @property
    def copyright(self) -> str:
        """

        Create appropriate copyright string

        """
        if self.client:
            return self.client
        return self.AUTHOR

    @property
    def long_description(self) -> str:
        """

        Read in README.md

        """
        return self.paths.readme.read_text()

    @property
    def version(self) -> str:
        """

        Read in the version string from file

        """
        return self.paths.version.read_text().strip()

    @property
    def find(self) -> Callable:
        """

        Use the appropriate package finding function from setuptools

        """
        from fmtr.tools import setup

        if self.paths.is_namespace:
            return setup.find_namespace_packages
        else:
            return setup.find_packages

    @property
    def packages(self) -> List[str]:
        """

        Fetch list of packages excluding canonical paths

        """
        excludes = list(Constants.PACKAGE_EXCLUDE_DIRS) + [f'{name}.*' for name in Constants.PACKAGE_EXCLUDE_DIRS if '*' not in name]
        packages = self.find(where=str(self.paths.repo), exclude=excludes)
        return packages

    @property
    def package_dir(self):
        """

        Needs to be relative apparently as absolute paths break during packaging

        """
        if self.paths.is_namespace:
            return {'': '.'}
        else:
            return None

    @property
    def package_data(self):
        """

        Default package data is just the version file

        """
        return {self.name: [Constants.FILENAME_VERSION]}

    @property
    def url(self) -> str:
        """

        Default to GitHub URL

        """
        return f'https://github.com/{self.org}/{self.name}'

    @property
    def data(self) -> Dict[str, Any]:
        """

        Generate data for use by setuptools

        """
        data = dict(
            name=self.name,
            version=self.version,
            author=self.author,
            author_email=self.AUTHOR_EMAIL,
            url=self.url,
            license=f'Copyright © {datetime.now().year} {self.copyright}. All rights reserved.',
            long_description=self.long_description,
            long_description_content_type='text/markdown',
            packages=self.packages,
            package_dir=self.package_dir,
            package_data=self.package_data,
            entry_points=dict(
                console_scripts=self.console_scripts,
            ),
            install_requires=self.dependencies.install,
            extras_require=self.dependencies.extras,
        ) | self.kwargs
        return data

    def setup(self):
        """

        Call setuptools.setup using generated data

        """

        from fmtr.tools import setup

        return setup.setup_setuptools(**self.data)

    def __repr__(self) -> str:
        """

        Show library name

        """
        return f'{self.__class__.__name__}("{self.name}")'

class Tools:
    """

    Helper for downstream libraries to specify lists of `fmtr.tools` extras

    """
    MASK = f'{Constants.LIBRARY_NAME}[{{extras}}]'

    def __init__(self, *extras):
        self.extras = extras

    def __str__(self):
        extras_str = ','.join(self.extras)
        return self.MASK.format(extras=extras_str)



class Dependencies:
    ALL = 'all'
    INSTALL = 'install'

    def __init__(self, **kwargs):
        self.dependencies = kwargs

    def resolve_values(self, key) -> List[str]:
        """

        Flatten a list of dependencies.

        """
        values_resolved = []
        values = self.dependencies[key]

        for value in values:
            if value == key or value not in self.dependencies:
                # Add the value directly if it references itself or is not a dependency key.
                values_resolved.append(str(value))
            else:
                # Recurse into nested dependencies.
                values_resolved += self.resolve_values(value)

        return values_resolved

    @cached_property
    def extras(self) -> Dict[str, List[str]]:
        """

        Flatten dependencies.

        """
        resolved = {key: self.resolve_values(key) for key in self.dependencies.keys()}
        resolved.pop(self.INSTALL, None)
        resolved[self.ALL] = list(set(chain.from_iterable(resolved.values())))
        return resolved

    @cached_property
    def install(self) -> List[str]:
        """

        Get install_requires

        """
        if self.INSTALL in self.dependencies:
            return self.resolve_values(self.INSTALL)
        else:
            return []


if __name__ == '__main__':
    ...
