import build
import pygit2 as vcs
import shutil
import tempfile
import twine.settings
from functools import cached_property
from mkdocs.__main__ import cli
from twine.commands.upload import upload as twine_upload

gh_deploy = cli.commands["gh-deploy"].callback



from fmtr.tools import environment_tools as env
from fmtr.tools import http_tools as http
from fmtr.tools.constants import Constants
from fmtr.tools.infrastructure_tools.project import Project
from fmtr.tools.inherit_tools import Inherit
from fmtr.tools.logging_tools import logger
from fmtr.tools.path_tools import Path


class Releaser(Inherit[Project]):
    """

    Manages the release process for a project.

    The release process consists of two main phases:

    1. Repository operations:
       - Fetch latest changes from remote
       - Increment version numbers in relevant files

    2. Distribution and publishing:
       - Create GitHub release (for both public and private repositories)
       - Build Python packages (wheel and sdist)
       - Upload to package indexes (private registry always, PyPI if configured)

    """

    @logger.instrument("Releasing {self.paths.name_ns}...")
    def run(self):
        self.repo.fetch()
        self.increment()
        self.repo.push()
        self.repo.fetch()

        if self.is_dockerhub:
            from fmtr.tools.infrastructure_tools.stack import ProductionPublic
            stack = self.stacks.cls[ProductionPublic]
            stack.build()
            stack.push()

        self.package()
        self.release()

    @property
    def message(self):
        return f"Release version {self.version}"

    @logger.instrument("Incrementing version numbers {self.repo.origin.url}...")
    def increment(self):
        """
        Increment version numbers in project files and create a new commit.

        This method updates version information across multiple project files (e.g., version file, Home Assistant addon config) and commits these changes to the main branch. It also creates a tag for the new version and fast-forwards the release branch to match main.

        The method uses a temporary git index file to stage changes independently from any existing staging in the working directory. This ensures that the release commit only includes version increment changes and is not affected by uncommitted work or previously staged files.

        Workflow:
        1. Creates a temporary index file based on the current committed state (HEAD of main)
        2. Applies version increment changes through configured incrementors
        3. Stages only the version-related changes in the temporary index
        4. Creates a new commit on the main branch with these changes
        5. Creates a git tag for the new version
        6. Fast-forwards the release branch to match the new main branch HEAD

        """
        repo = self.repo

        main_ref = repo.lookup_reference("refs/heads/main")
        parent = main_ref.peel(vcs.Commit)

        git_dir = Path(repo.path)  # .../.git/
        src_index = git_dir / "index"

        with tempfile.TemporaryDirectory(prefix=f"{self.paths.name_ns}-index-") as path_dir:
            paths = Path(path_dir) / "index"
            paths.write_bytes(src_index.read_bytes())

            index = vcs.Index(str(paths))
            index.read_tree(parent.tree)

            for incrementor in self.incrementors:
                paths = incrementor.apply()
                if not paths:
                    continue

                if not isinstance(paths, list):
                    paths = [paths]

                for path in paths:
                    rel = str(Path(path).relative_to(self.paths.repo))
                    blob_id = repo.create_blob_fromworkdir(rel)

                    try:
                        mode = parent.tree[rel].filemode
                    except KeyError:
                        mode = vcs.GIT_FILEMODE_BLOB

                    index.add(vcs.IndexEntry(rel, blob_id, mode))

            index.write()
            tree = index.write_tree(repo)

            commit_id = repo.create_commit(
                main_ref.name,
                repo.default_signature,
                repo.default_signature,
                self.message,
                tree,
                [parent.id],
            )

        repo.create_tag(
            self.tag,
            commit_id,
            vcs.GIT_OBJECT_COMMIT,
            repo.default_signature,
            self.message,
        )

        branch_name = "release"
        ref_name = f"refs/heads/{branch_name}"

        try:
            release_ref = repo.lookup_reference(ref_name)
        except KeyError:
            target = repo.head.peel(vcs.Commit)
            release_ref = repo.create_branch(branch_name, target)

        release_commit = release_ref.peel(vcs.Commit)

        if repo.merge_base(commit_id, release_commit.id) != release_commit.id:
            raise RuntimeError("release has diverged from main")

        release_ref.set_target(commit_id)

        return commit_id

    @cached_property
    def path(self):
        return Path.temp() / self.name

    @cached_property
    def token(self):
        return env.get(Constants.GITHUB_TOKEN_KEY)

    @cached_property
    def incrementors(self):
        return [IncrementorVersion(self), IncrementorHomeAssistantAddon(self), IncrementorChangelog(self)]

    @cached_property
    def packagers(self):
        return [PackageWheel(self), PackageSourceDistribution(self)]

    @cached_property
    def releases(self):
        releases = [
            ReleaseGithub(self),
            ReleasePackageIndexPrivate(self),
            ReleaseDocumentation(self)

        ]

        if self.is_pypi:
            release = ReleasePackageIndexPublic(self)
            releases.append(release)

        return releases

    def release(self):
        for release in self.releases:
            release.release()


    def package(self):
        if self.path.exists():
            logger.warning(f"Package directory already exists: {self.path}. Will be removed.")
            shutil.rmtree(self.path)

        self.path.mkdir(parents=True)

        for packager in self.packagers:
            packager.package()


class Incrementor(Inherit[Releaser]):

    def apply(self) -> Path | None:
        raise NotImplementedError


class IncrementorVersion(Incrementor):

    @cached_property
    def path(self):
        return self.paths.version

    @logger.instrument('Incrementing version file "{self.path}"...')
    def apply(self) -> Path | list[Path] | None:
        path = self.paths.version
        path.write_text(str(self.version))
        project = self.inherit_root
        project.incremented = True
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
        data['version'] = str(self.version)
        self.path.write_yaml(data)
        return self.path


class IncrementorChangelog(Incrementor):

    @cached_property
    def path(self):
        return self.paths.docs_changelog

    @logger.instrument('Incrementing Changelog "{self.path}"...')
    def apply(self) -> Path | list[Path] | None:
        if not self.path.exists():
            logger.warning(f"New changelog not found: {self.path}. Skipping.")
            return None

        paths = []
        logger.info(f"Version tagging Changelog: {self.path}")
        path_version = self.path.with_stem(f'{self.version}')
        self.path.rename(path_version)
        paths.append(path_version)

        src = Path(path_version).relative_to(self.paths.repo)
        dest = self.paths.changelog

        dest.unlink(missing_ok=True)
        dest.symlink_to(src)

        paths.append(dest)
        return paths





class Packager(Inherit[Releaser]):
    """
    
    Base class for packaging operations.
    
    """
    TYPE = None

    def package(self):
        builder = build.ProjectBuilder(str(self.paths.repo))
        with logger.span(f'Building {self.TYPE} distribution...'):
            path = builder.build(self.TYPE, str(self.path))
            logger.info(f'Build complete: {path}')


class PackageWheel(Packager):
    """
    
    Package as Python wheel.
    
    """
    TYPE = 'wheel'


class PackageSourceDistribution(Packager):
    """
    
    Package as source distribution.
    
    """
    TYPE = 'sdist'


class Release(Inherit[Releaser]):
    """
    
    Base class for release operations.
    
    """
    def release(self):
        raise NotImplementedError


class ReleaseGithub(Release):
    """
    
    Release to GitHub.
    
    """

    def release(self):
        url = f"https://api.github.com/repos/{self.org}/{self.paths.name_ns}/releases"
        name = f'Release {self.tag}'

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        payload = {
            "tag_name": self.tag,
            "name": name,
            "body": name,
            "draft": False,
            "prerelease": self.is_pre
        }

        with logger.span(f'Creating release "{name}"...'):
            response = http.client.post(url, json=payload, headers=headers)

        response.raise_for_status()

        data = response.json()
        url = data['html_url']
        logger.info(f"Release created: {url}")


class ReleasePackageIndex(Release):
    """
    
    Base class for package index releases.
    
    """
    
    TOKEN_KEY = None
    URL = None
    USERNAME = None
    NAME = None

    @cached_property
    def token(self):
        return env.get(self.TOKEN_KEY)

    @cached_property
    def settings(self):
        return twine.settings.Settings(
            repository_name=self.NAME,
            repository_url=self.URL,
            username=self.USERNAME,
            password=self.token,
            non_interactive=True,
            verbose=True
        )

    def release(self):
        with logger.span(f'Uploading package to PyPI index ({self.URL}) as {self.USERNAME}...'):
            twine_upload(self.settings, [f'{self.path}/*'])


class ReleasePackageIndexPrivate(ReleasePackageIndex):
    """
    
    Release to private package index.
    
    """
    TOKEN_KEY = Constants.PACKAGE_INDEX_PRIVATE_TOKEN_KEY
    URL = Constants.PACKAGE_INDEX_PRIVATE_URL
    USERNAME = Constants.ORG_NAME


class ReleasePackageIndexPublic(ReleasePackageIndex):
    """
    
    Release to public package index, namely PyPI.
    
    """
    TOKEN_KEY = Constants.PACKAGE_INDEX_PUBLIC_TOKEN_KEY
    URL = None
    USERNAME = '__token__'
    NAME = "pypi"


class ReleaseDocumentation(Release):

    @property
    def data(self):
        import io

        from mkdocs.config import load_config
        from material.extensions.emoji import twemoji, to_svg

        return dict(
            config_file=io.StringIO(""),
            site_dir='site',
            docs_dir=str(self.paths.docs),

            site_name=self.paths.name_ns,
            theme={
                "name": "material",
                "features": [
                    "content.code.annotate",
                    "content.code.copy",
                ],
            },
            plugins=[
                "search",
                {"include_dir_to_nav": {"reverse_sort_file": True}},
                {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "options": {
                                    "show_source": True,
                                }
                            }
                        }
                    }
                },
            ],
            markdown_extensions=[
                "admonition",
                "attr_list",
                "md_in_html",
                "pymdownx.superfences",
                {"pymdownx.highlight": {"pygments_lang_class": True}},
                {"pymdownx.snippets": {"check_paths": True}},

                {"pymdownx.tabbed": {"alternate_style": True}},
                {"pymdownx.emoji": {"emoji_index": twemoji, "emoji_generator": to_svg}},
            ],
            nav=[
                {"Home": "index.md"},
                {"Changelog": "changelog/"},
            ],
            extra={
                "version": {"provider": "mike"},
            },
        )

    @property
    def message(self):
        return f"Release documentation version {self.version}"

    def deploy(self):
        result = gh_deploy(
            clean=True,
            message=self.message,
            remote_branch="docs",
            remote_name="origin",
            force=True,
            no_history=False,
            ignore_version=False,
            shell=False,
            **self.data
        )
        return result

    def release(self):
        with self.paths.repo.chdir:
            self.deploy()
        self
