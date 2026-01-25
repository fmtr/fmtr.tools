from functools import cached_property

from fmtr.tools import version_tools
from fmtr.tools.constants import Constants
from fmtr.tools.infrastructure_tools.repository import Repository
from fmtr.tools.inherit_tools import Inherit
from fmtr.tools.iterator_tools import IndexList
from fmtr.tools.path_tools import PackagePaths
from fmtr.tools.setup_tools import SetupPaths


class Project:
    """

    Represents a canonical project with associated settings, runtime configuration, and paths.

    """

    def __init__(self, name, port=None, services=None, scripts=None, base='python', entrypoint=None, hostname='ws.lan', channel='dev', extras=None, is_pypi=False, is_dockerhub=False, nav=None, pinned=None):

        # project settings:
        self.services = services or []
        self.scripts = scripts or []
        self.base = base
        self.port = port
        self.entrypoint = entrypoint
        self.nav = nav

        self.is_pypi = is_pypi
        self.is_dockerhub = is_dockerhub

        self.incremented = False

        # runtime:
        self.hostname = hostname
        self.channel = channel
        self.extras = extras or ['all']

        self.name = name

        sep = '.'  # todo move all to SetupPaths.package_paths - or merge generally.
        if sep in name:
            org, package = name.split(sep)
            org_singleton = None
        else:
            org = None
            org_singleton = Constants.ORG_NAME

        setup_paths = SetupPaths(path=PackagePaths.dev / 'repo' / name, org=org)
        self.paths = PackagePaths(path=setup_paths.path, org_singleton=org_singleton)

        self.versions = Versions(self, pinned=pinned)



    @cached_property
    def repo(self):
        return Repository(self.paths.repo, project=self)

    @property
    def version(self):

        return self.versions.new

    @property
    def tag(self):
        return f'v{self.version}'


    @cached_property
    def org(self):
        return self.paths.org

    @cached_property
    def package(self):
        return self.paths.name

    @cached_property
    def stacks(self):
        from fmtr.tools.infrastructure_tools.stack import Stack, Development, ProductionPrivate, ProductionPublic
        classes = [Development, ProductionPrivate, ProductionPublic]
        stacks = IndexList[Stack](cls(self) for cls in classes)
        return stacks

    @cached_property
    def releaser(self):
        from fmtr.tools.infrastructure_tools.releaser import Releaser
        return Releaser(self)

    @cached_property
    def name_components(self):
        return self.name.split('.')

    def join_name(self, sep):
        return sep.join(self.name_components)

    @cached_property
    def name_dash(self):
        return self.join_name('-')

    @cached_property
    def extras_str(self):
        return ','.join(self.extras)

    @cached_property
    def scripts_str(self):
        return ' '.join(self.scripts)


class Versions(Inherit[Project]):

    def __init__(self, project: Project, pinned: str | None = None):
        super().__init__(project)
        self.old = self.get()

        self.pinned = None
        if pinned:
            self.pinned = version_tools.Version.parse(pinned)

    def get(self):
        ver_str = self.paths.version.read_text().strip()

        version_obj = version_tools.parse(ver_str)
        return version_obj

    @property
    def new(self):

        version_obj = self.get()

        if self.incremented:
            return version_obj

        version_obj = self.pinned or self.bump(version_obj)

        return version_obj

    def bump(self, version):
        if version.prerelease:
            return version.bump_prerelease()
        return version.bump_patch()

    @property
    def is_pre(self):
        return bool(self.new.prerelease)
