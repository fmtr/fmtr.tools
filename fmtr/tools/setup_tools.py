from itertools import chain

from datetime import datetime
from functools import cached_property
from setuptools import find_namespace_packages, find_packages
from typing import List, Dict

from fmtr.tools.constants import Constants
from fmtr.tools.path_tools import Path
from fmtr.tools.path_tools.path_tools import PathsBase, path


class SetupPaths(PathsBase):
    """

    Canonical paths for a package.

    """

    SKIP_DIRS = {'data'}

    def __init__(self, path=None):

        """

        Use calling module path as default path, if not otherwise specified.

        """
        if not path:
            path = self.from_caller()

        self.repo = Path(path)

    @property
    def path(self):
        if self.is_namespace:
            return self.repo / self.org / self.name
        else:
            return self.repo / self.name

    @property
    def readme(self):
        return self.repo / 'README.md'

    @property
    def version(self):
        return self.path / Constants.FILENAME_VERSION

    @cached_property
    def layout(self):

        directories = [
            dir for dir in self.repo.iterdir()
            if dir.is_dir() and not dir.name.startswith('.') and dir.name not in self.SKIP_DIRS
        ]

        if len(directories) != 1:
            raise ValueError(f'Expected exactly one directory in "{path}", found {','.join(directories)}')

        target = next(iter(directories))

        contents = list(target.iterdir())
        if len(contents) == 1 and (item := next(iter(contents))).is_dir():
            return True, target.name, item.name

        else:
            return False, None, target.name

    @property
    def is_namespace(self) -> str:
        is_namespace, org, name = self.layout
        return is_namespace

    @property
    def org(self) -> str:
        is_namespace, org, name = self.layout
        return org

    @property
    def name(self) -> str:
        is_namespace, org, name = self.layout
        return name


class Setup:
    AUTHOR = 'Frontmatter'
    AUTHOR_EMAIL = 'innovative.fowler@mask.pro.fmtr.dev'

    paths = SetupPaths(path=Path(__file__).absolute().parent.parent.parent)

    def __init__(self, dependencies, console_scripts=None, client=None, **kwargs):

        self.client = client
        self.kwargs = kwargs
        self.dependencies = dependencies
        self.paths

        self.console_scripts = console_scripts

    def get_entrypoint_path(self, key, value):
        if value:
            return f'{self.name}.{value}:{key}'
        else:
            return f'{self.name}:{key}'

    @property
    def entrypoints(self):
        if self.console_scripts:
            return dict(
                console_scripts=[f'{key} = {self.get_entrypoint_path(key, value)}' for key, value in self.console_scripts.items()],
            )
        else:
            return dict()

    @property
    def name(self):
        if self.paths.is_namespace:
            return f'{self.paths.org}.{self.paths.name}'
        return self.paths.name

    @property
    def author(self):
        if self.client:
            return f'{self.AUTHOR} on behalf of {self.client}'
        return self.AUTHOR

    @property
    def copyright(self):
        if self.client:
            return self.client
        return self.AUTHOR

    @property
    def long_description(self):

        return self.paths.readme.read_text()

    @property
    def version(self):
        return self.paths.version.read_text().strip()

    @property
    def packages(self):
        if self.paths.is_namespace:
            return find_namespace_packages(where=str(self.paths.repo))
        else:
            return find_packages(where=str(self.paths.repo))

    @property
    def package_dir(self):
        if self.paths.is_namespace:
            return {'': str(self.paths.repo)}
        else:
            return None

    @property
    def package_data(self):
        return {self.name: [Constants.FILENAME_VERSION]}

    @property
    def url(self):
        return f'https://github.com/{self.paths.org}/{self.paths.name}'

    def get_data_setup(self):
        return dict(
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
            entry_points=self.entrypoints,
            install_requires=self.dependencies.install,
            extras_require=self.dependencies.extras,
        ) | self.kwargs


class Entrypoints:
    ALL = 'all'
    INSTALL = 'install'

    def __init__(self, console_scripts=None, **kwargs):
        self.kwargs = kwargs
        self._console_scripts = console_scripts

    @property
    def console_scripts(self):
        return [f'{key} = {value}:{key}' for key, value in self._console_scripts.items()]

    @property
    def data(self):
        return dict(
            console_scripts=self.console_scripts,
        ) | self.kwargs


class Dependencies:
    ALL = 'all'
    INSTALL = 'install'

    def __init__(self, **kwargs):
        self.dependencies = kwargs

    def resolve_values(self, key) -> List[str]:
        """

        Flatten a list of values.

        """
        values_resolved = []
        values = self.dependencies[key]

        for value in values:
            if value == key or value not in self.dependencies:
                # Add the value directly if it references itself or is not a dependency key.
                values_resolved.append(value)
            else:
                # Recurse into nested dependencies.
                values_resolved += self.resolve_values(value)

        return values_resolved

    @property
    def extras(self) -> Dict[str, List[str]]:
        """

        Flatten dependencies.

        """
        resolved = {key: self.resolve_values(key) for key in self.dependencies.keys()}
        resolved.pop(self.INSTALL, None)
        resolved[self.ALL] = list(set(chain.from_iterable(resolved.values())))
        return resolved

    @property
    def install(self):
        return self.resolve_values(self.INSTALL)


if __name__ == '__main__':
    ds = Dependencies(
        install=['version', 'yaml'],

        yaml=['yamlscript', 'pyyaml'],
        logging=['logfire', 'version'],
        version=['semver', 'av'],
        av=['av']
        # Add the rest of your dependencies...
    )

    ds

    setup = Setup(
        # client='Acme',
        dependencies=ds,
        description='some tools test',
        console_scripts=dict(
            cache_hfh='console_script_tools',
            test=None,
        )
    )
    data = setup.get_data_setup()
    data
