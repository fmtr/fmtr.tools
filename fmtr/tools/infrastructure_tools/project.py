from functools import cached_property

from fmtr.tools.constants import Constants
from fmtr.tools.infrastructure_tools.repository import Repository
from fmtr.tools.iterator_tools import IndexList
from fmtr.tools.path_tools import PackagePaths
from fmtr.tools.setup_tools import SetupPaths


class Project:

    def __init__(self, name, port=None, services=None, base='python', entrypoint='launch', hostname='ws.lan', channel='dev', extras=None, is_pypi=False):

        # project settings:
        self.services = services or []
        self.base = base
        self.port = port
        self.entrypoint = entrypoint
        self.is_pypi = is_pypi

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

    @cached_property
    def repo(self):
        return Repository(self.paths.repo, project=self)

    @cached_property
    def org(self):
        return self.paths.org

    @cached_property
    def package(self):
        return self.paths.name

    @cached_property
    def stacks(self):
        from fmtr.tools.infrastructure_tools.stack import Stack
        stacks = IndexList[Stack](cls(self) for cls in Stack.get_all())
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
