import pygit2 as vcs
from functools import cached_property
from typing import Any

from fmtr.tools import version_tools as version
from fmtr.tools.inherit_tools import Inherit
from fmtr.tools.logging_tools import logger
from fmtr.tools.path_tools import Path


class Repository(vcs.Repository):

    def __init__(self, path: Path, project: Any):
        super().__init__(str(path))
        self.project = project

    @cached_property
    def data(self):
        return VersionData(self)

    @cached_property
    def tags(self):
        return Tags(self)

    @property
    def remote(self):
        return self.repo.remotes["origin"]

    @property
    def keypair(self):
        return vcs.Keypair("git", self.SSH_DIR / "id_rsa.pub", self.SSH_DIR / "id_rsa", passphrase=None)

    @property
    def callbacks(self):
        return vcs.RemoteCallbacks(credentials=self.keypair)

    @property
    def specs(self):
        return [
            "+refs/heads/*:refs/remotes/origin/*",
            "+refs/tags/*:refs/tags/*",
        ]

    @logger.instrument('Fetching from repo {self.remote.url}...')
    def fetch(self):
        return self.remote.fetch(self.specs, callbacks=self.callbacks)


class VersionData(Inherit[Repository]):

    @cached_property
    def current(self):
        ver_str = self.project.paths.version.read_text().strip()

        version_obj = version.parse(ver_str)
        return version_obj

    @property
    def new(self):
        version_new = self.current.bump_patch()  # todo: inc prelrease, if it's pre, else bump patch.
        return version_new

    @property
    def is_pre(self):
        return bool(self.new.prerelease)


class Tags(Inherit[Repository]):

    @property
    def new(self):
        return f"v{self.project.data.new}"

    @property
    def current(self):
        return f"v{self.project.data.current}"

    def get_tags(self):
        for ref in self.references:
            path = Path(ref)
            if path.parent.name == 'tags':
                yield path.name

    @property
    def all(self):
        return set(self.get_tags())
