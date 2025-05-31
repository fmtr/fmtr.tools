import sys
from datetime import datetime
from functools import cached_property
from itertools import chain
from typing import List, Dict

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
    def readme(self):
        return self.repo / 'README.md'

    @property
    def version(self):
        return self.path / Constants.FILENAME_VERSION

    @cached_property
    def path(self):

        from fmtr.tools import setup

        if self.org:
            base = self.org
        else:
            base = self.repo

        directories = [base / dir for dir in setup.find_packages(base)]

        if len(directories) != 1:
            dirs_str = ', '.join([str(dir) for dir in directories])
            raise ValueError(f'Expected exactly one directory in {self.repo}, found {dirs_str}')

        package = next(iter(directories))
        return package

    @property
    def org(self):
        if not self.org_name:
            return False
        org = self.repo / self.org_name
        if not org.is_dir():
            return False
        return org

    @property
    def is_namespace(self) -> bool:
        return bool(self.org)

    @property
    def name(self) -> str:
        return self.path.stem


class Setup(FromCallerMixin):
    AUTHOR = 'Frontmatter'
    AUTHOR_EMAIL = 'innovative.fowler@mask.pro.fmtr.dev'

    REQUIREMENTS_ARG = 'requirements'
    SKIP_DIRS = {'data', 'build', 'dist', '.*', '*egg-info*'}

    def __init__(self, dependencies, paths=None, org=Constants.ORG_NAME, console_scripts=None, client=None, do_setup=True, **kwargs):

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
        self.console_scripts = console_scripts

        if do_setup:
            self.setup()

    def get_requirements_extras(self):
        if self.REQUIREMENTS_ARG not in sys.argv:
            return None

        extras_str = sys.argv[-1]
        extras = extras_str.split(',')
        return extras

    def print_requirements(self):
        reqs = []
        reqs += self.dependencies.install

        for extra in sys.argv[-1].split(','):
            reqs += self.dependencies.extras[extra]
        reqs = '\n'.join(reqs)
        print(reqs)



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
    def find(self):

        from fmtr.tools import setup

        if self.paths.is_namespace:
            return setup.find_namespace_packages
        else:
            return setup.find_packages

    @property
    def packages(self):

        excludes = list(self.SKIP_DIRS) + [f'{name}.*' for name in self.SKIP_DIRS if '*' not in name]

        packages = self.find(where=str(self.paths.repo), exclude=excludes)
        return packages

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

    @property
    def data(self):
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
            entry_points=self.entrypoints,
            install_requires=self.dependencies.install,
            extras_require=self.dependencies.extras,
        ) | self.kwargs
        return data

    def setup(self):

        from fmtr.tools import setup

        return setup.setup_setuptools(**self.data)


class Tools:
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

        Flatten a list of values.

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
