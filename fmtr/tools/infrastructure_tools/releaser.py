import pygit2 as vcs
from functools import cached_property

from fmtr.tools.infrastructure_tools.project import Project
from fmtr.tools.inherit_tools import Inherit
from fmtr.tools.logging_tools import logger
from fmtr.tools.path_tools import Path


class Releaser(Inherit[Project]):
    """

    Two steps (which I suppose should run for ALL projects:

    # repo-related: fetch, increment, tag, push.
    # do gh release create. should always make a release, even on private.




    """

    SSH_DIR = Path().home() / ".ssh"

    def run(self):

        self.fetch()
        self.increment()
        # self.tagger.apply()
        self

        # todo next run stuff like publishing to pypi.

    @cached_property
    def incrementors(self):
        return [IncrementorVersion(self), IncrementorHomeAssistantAddon(self)]

    @cached_property
    def tagger(self):
        return Tagger(self)

    @logger.instrument('Incrementing version numbers {self.remote.url}...')
    def increment(self):

        # # Abort if tag already exists (same logic as before)
        # if self.tags.new in self.tags.all:
        #     logger.warning(f"Tag already exists: {self.tags.new}. Will not increment version.")
        #     return

        repo = self.repo
        index = repo.index

        # todo remove any files that are already added?

        # --- apply version increments ---
        for inc in self.incrementors:
            path = inc.apply()
            if not path:
                continue
            index.add(str(path.relative_to(self.paths.repo)))

        index.write()
        tree = index.write_tree()

        # --- commit on main ---
        main_ref = repo.lookup_reference('refs/heads/main')
        parent = main_ref.peel(vcs.Commit)

        commit_id = repo.create_commit(
            main_ref.name,
            repo.default_signature,
            repo.default_signature,
            "Increment version numbers",
            tree,
            [parent.id],
        )

        # --- OPTIONAL TAG (left commented for debugging) ---
        # repo.create_tag(
        #     self.tag,
        #     commit_id,
        #     vcs.GIT_OBJECT_COMMIT,
        #     repo.default_signature,
        #     f"Release version {self.version}",
        # )

        # --- fast-forward release to main ---
        release_ref = repo.lookup_reference('refs/heads/release')
        release_commit = release_ref.peel(vcs.Commit)

        # safety check: only fast-forward if release is behind main
        if repo.merge_base(commit_id, release_commit.id) != release_commit.id:
            raise RuntimeError("release has diverged from main")

        release_ref.set_target(commit_id)

        return commit_id


class Incrementor(Inherit[Releaser]):

    def apply(self) -> Path | None:
        raise NotImplementedError


class IncrementorVersion(Incrementor):

    @cached_property
    def path(self):
        return self.paths.version

    @logger.instrument('Incrementing version file "{self.path}"...')
    def apply(self) -> Path | None:
        path = self.paths.version
        path.write_text(str(self.data.new))
        return path


class IncrementorHomeAssistantAddon(Incrementor):

    @cached_property
    def path(self):
        return self.paths.ha_addon_config

    @logger.instrument('Incrementing Home Assistant Add-On version "{self.path}"...')
    def apply(self) -> Path | None:
        if not self.path.exists():
            logger.warning(f"Home Assistant Add-On config file not found: {self.path}. Skipping.")
            return None

        data = self.path.read_yaml()
        data['version'] = str(self.data.new)
        self.path.write_yaml(data)
        return self.path


class Tagger(Inherit[Releaser]):
    MASK = "Release version {self.data.new}"

    def apply(self):
        commit = self.repo.lookup_reference('refs/heads/main').peel(vcs.Commit)

        msg = self.MASK.format(self=self)
        self.repo.create_tag(
            self.tags.new,
            commit.id,
            vcs.GIT_OBJECT_COMMIT,
            self.repo.default_signature,
            msg,
        )
