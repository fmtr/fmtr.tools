import os
import re
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain, product
from pathlib import Path
from tempfile import gettempdir
from typing import Self
from typing import Union, Any

from fmtr.tools.constants import Constants
from fmtr.tools.platform_tools import is_wsl

WIN_PATH_PATTERN = r'''([a-z]:(\\|$)|\\\\)'''
WIN_PATH_RX = re.compile(WIN_PATH_PATTERN, flags=re.IGNORECASE)


class WSLPathConversionError(EnvironmentError):
    """

    Error to raise if WSL path conversion fails.

    """


class Path(type(Path())):
    """

    Custom path object aware of WSL paths, with some additional read/write methods

    """

    def __new__(cls, *segments: Union[str, Path], convert_wsl: bool = True, **kwargs):
        """

        Intercept arguments to detect whether WSL conversion is required.

        """
        if convert_wsl and len(segments) == 1 and is_wsl() and cls.is_abs_win_path(*segments):
            segments = [cls.from_wsl(*segments)]

        return super().__new__(cls, *segments, **kwargs)

    @classmethod
    def is_abs_win_path(cls, path: Union[str, Path]) -> bool:
        """

        Infer if the current path is an absolute Windows path.

        """
        path = str(path)
        return bool(WIN_PATH_RX.match(path))

    @classmethod
    def from_wsl(cls, path: Union[str, Path]) -> bool:  # pragma: no cover
        """

        Call `wslpath` to convert the path to its Unix equivalent.

        """
        result = subprocess.run(['wslpath', '-u', str(path)], capture_output=True, text=True)

        if result.returncode:
            msg = f'Could not convert Windows path to Unix equivalent: "{path}"'
            raise WSLPathConversionError(msg)

        path_wsl = result.stdout.strip()
        path_wsl = cls(path_wsl, convert_wsl=False)
        return path_wsl

    @classmethod
    def package(cls) -> 'Path':
        """

        Get path to originating module (e.g. directory containing .py file).

        """
        from fmtr.tools.inspection_tools import get_call_path
        path = get_call_path(offset=2).absolute().parent
        return path

    @classmethod
    def module(cls) -> 'Path':
        """

        Get path to originating module (i.e. .py file).

        """
        from fmtr.tools.inspection_tools import get_call_path
        path = get_call_path(offset=2).absolute()
        return path

    @classmethod
    def temp(cls) -> 'Path':
        """

        Get path to temporary directory.

        """
        return cls(gettempdir())

    def write_json(self, obj) -> int:
        """

        Write the specified object to the path as a JSON string

        """
        from fmtr.tools import json
        json_str = json.to_json(obj)
        return self.write_text(json_str, encoding=Constants.ENCODING)

    def read_json(self) -> Any:
        """

        Read JSON from the file and return as a Python object

        """
        from fmtr.tools import json
        json_str = self.read_text(encoding=Constants.ENCODING)
        obj = json.from_json(json_str)
        return obj

    def write_yaml(self, obj) -> int:
        """

        Write the specified object to the path as a JSON string

        """
        from fmtr.tools import yaml
        yaml_str = yaml.to_yaml(obj)
        return self.write_text(yaml_str, encoding=Constants.ENCODING)

    def read_yaml(self) -> Any:
        """

        Read YAML from the file and return as a Python object

        """
        from fmtr.tools import yaml
        yaml_str = self.read_text(encoding=Constants.ENCODING)
        obj = yaml.from_yaml(yaml_str)
        return obj

    def mkdirf(self):
        """

        Convenience method for creating directory with parents

        """
        return self.mkdir(parents=True, exist_ok=True)

    def with_suffix(self, suffix: str) -> 'Path':
        """

        Pathlib doesn't add a dot prefix, but then errors if you don't provide one, which feels rather obnoxious.

        """
        if not suffix.startswith('.'):
            suffix = f'.{suffix}'
        return super().with_suffix(suffix)

    def get_conversion_path(self, suffix: str) -> 'Path':
        """

        Fetch the equivalent path for a different format in the standard conversion directory structure.
        .../xyz/filename.xyx -> ../abc/filename.abc

        """

        old_dir = self.parent.name

        if old_dir != self.suffix.removeprefix('.'):
            raise ValueError(f"Expected parent directory '{old_dir}' to match file extension '{suffix}'")

        new = self.parent.parent / suffix / f'{self.stem}.{suffix}'
        return new

    @property
    def exist(self):
        """

        Exists as property

        """
        return super().exists()

    @classmethod
    def app(cls):
        """

        Convenience method for getting application paths

        """
        from fmtr.tools import path
        return path.AppPaths()

    @property
    def type(self):
        """

        Infer file type, extension, etc.

        """
        if not self.exists():
            return None
        from fmtr.tools import path
        kind = path.guess(str(self.absolute()))
        return kind

    @property
    def children(self) -> list[Self]:
        """

        Recursive children property

        """
        if not self.is_dir():
            return None
        return sorted(self.iterdir(), key=lambda x: x.is_dir(), reverse=True)

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        """

        Support Pydantic de/serialization and validation

        TODO: Ideally these would be a mixin in dm, but then we'd need Pydantic to use it. Split dm module into Pydantic depts and other utils and import from there.

        """
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(
            cls.__deserialize_pydantic__,
            serialization=core_schema.plain_serializer_function_ser_schema(cls.__serialize_pydantic__),
        )

    @classmethod
    def __serialize_pydantic__(cls, self) -> str:
        """

        Serialize to string

        """
        return str(self)

    @classmethod
    def __deserialize_pydantic__(cls, data) -> Self:
        """

        Deserialize from string

        """
        if isinstance(data, cls):
            return data
        return cls(data)

    @property
    def chdir(self):
        """

        Return change dir context manager

        """
        return chdir(self)

class FromCallerMixin:
    """


    """

    def from_caller(self):
        from fmtr.tools.inspection_tools import get_call_path
        path = get_call_path(offset=3).parent
        return path


@dataclass
class Metadata:
    path: Path = field(init=False)

    version: str
    port: int | None = None
    entrypoint: str | None = None
    scripts: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    docs: dict = field(default_factory=dict)
    setup: dict = field(default_factory=dict)

    is_pypi: bool = False
    is_dockerhub: bool = False

    @classmethod
    def read(cls, path: Path) -> Self:
        data = path.read_json()
        self = cls(**data)
        self.path = path
        return self

    def write(self):
        from dataclasses import asdict
        data = asdict(self)
        return self.path.write_json(data)

    @property
    def version_obj(self):
        from fmtr.tools.version_tools import Version
        version = Version.parse(self.version)
        return version

class PackagePaths(FromCallerMixin):
    """

    Canonical paths for a package.

    """

    dev = Path('/') / 'opt' / 'dev'
    dev_repo = dev / 'repo'
    data_global = dev / Constants.DIR_NAME_DATA

    def __init__(self, path: Path | None = None):
        """

        Use calling module path as default path, if not otherwise specified.

        """

        data = PathsSearchData.from_caller(path or self.from_caller())

        self.path = data.path
        self.repo = data.repo
        self.name = data.name
        self.org = data.org

    @cached_property
    def metadata(self) -> Metadata:
        """

        Package metadata

        """
        return Metadata.read(self.path / Constants.FILENAME_META)

    @property
    def is_dev(self) -> bool:
        """

        Is the package in the dev directory - as opposed to `site-packages` etc?

        """
        return self.path.is_relative_to(self.dev)

    @property
    def is_namespace(self) -> bool:
        """

        If organization is not present, then the package is a namespace.

        """
        return bool(self.org)

    @property
    def name_ns(self) -> str:
        """

        Name of namespace package.

        """

        if self.is_namespace:
            return f'{self.org}.{self.name}'
        else:
            return self.name


    @property
    def version(self) -> Path:
        """

        Path of version file.

        """
        return self.path / Constants.FILENAME_VERSION

    @property
    def data(self) -> Path:
        """

        Path of project-specific data directory.

        """
        return self.dev / Constants.DIR_NAME_REPO / self.name_ns / Constants.DIR_NAME_DATA

    @property
    def cache(self) -> Path:
        """

        Path of cache directory.

        """

        return self.data / Constants.DIR_NAME_CACHE

    @property
    def artifact(self) -> Path:
        """

        Path of project-specific artifact directory

        """

        return self.data / Constants.DIR_NAME_ARTIFACT

    @property
    def source(self) -> Path:
        """

        Path of project-specific source directory

        """

        return self.data / Constants.DIR_NAME_SOURCE

    @property
    def settings(self) -> Path:
        """

        Path of settings file.

        """
        return self.data / Constants.FILENAME_CONFIG

    @property
    def hf(self) -> Path:
        """

        Path of HuggingFace directory

        """
        return self.artifact / Constants.DIR_NAME_HF

    @property
    def docs(self) -> Path:
        """

        Path of docs directory

        """
        return self.repo / Constants.DOCS_DIR

    @property
    def docs_config(self) -> Path:
        """

        Path of docs config file

        """
        return self.repo / Constants.DOCS_CONFIG_FILENAME

    @property
    def ha_config(self) -> Path:
        """

        Path of Home Assistant config file

        """
        return self.repo / 'ha' / 'config.yaml'

    @property
    def ha_addon(self) -> Path:
        """

        Path of Home Assistant add-on

        """
        return self.repo / 'ha' / 'addon'

    @property
    def ha_addon_changelog(self) -> Path:
        """

        Path of Home Assistant add-on changelog

        """
        return self.ha_addon / 'CHANGELOG.md'

    @property
    def ha_addon_config(self) -> Path:
        """

        Path of Home Assistant add-on config file

        """
        return self.ha_addon / 'config.yaml'

    @property
    def changelog(self) -> Path:
        """

        Path of repo changelog

        """
        return self.repo / 'CHANGELOG.md'

    @property
    def docs_changelog(self) -> Path:
        """

        Path of docs latest changelog

        """
        return self.docs / 'changelog' / 'changelog.md'

    @property
    def readme(self) -> Path:
        """

        Path of the README file.

        """
        return self.repo / 'README.md'

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
    def scripts(self) -> Path:
        """

        Paths of shell scripts

        """

        return self.repo / Constants.SCRIPTS_DIR

    def __repr__(self) -> str:
        """

        Show base path in repr.

        """
        return f'{self.__class__.__name__}("{self.path}")'

@contextmanager
def chdir(path: Path):
    """

    Set CWD temporarily using a context manager

    """
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(prev)


root = Path('/')


@dataclass
class PathsSearchData:
    path: Path
    repo: Path
    name: str
    org: str | None

    SETUP_FILE = "setup.py"

    @classmethod
    def from_caller(cls, path_caller: Path) -> Self:

        if (path_caller / cls.SETUP_FILE).exists():
            return cls.from_repo(path_caller)

        path_repo = cls.find_repo(path_caller)
        return cls.from_repo(path_repo)

    @classmethod
    def from_repo(cls, path_repo: Path) -> Self:

        masks = "*/{name}", "*/*/{name}"
        names = Constants.FILENAME_VERSION, Constants.FILENAME_META
        patterns = [mask.format(name=name) for mask, name in product(masks, names)]

        targets = chain.from_iterable(path_repo.glob(pattern) for pattern in patterns)
        targets = list(targets)

        if len(targets) != 1:
            raise FileNotFoundError(f"Expected exactly 1 of {names} at depth 1 or 2 under {path_repo}, found {len(targets)}: {targets}")

        path = next(iter(targets)).parent
        parts = path.relative_to(path_repo).parts

        if len(parts) == 2:
            org, name = parts
        else:
            org = None
            name = next(iter(parts))

        return cls(path=path, repo=path_repo, name=name, org=org)

    @classmethod
    def find_repo(cls, path_package: Path) -> Path:

        cur = path_package
        while True:
            if (cur / cls.SETUP_FILE).exists():
                return cur
            if cur.parent == cur:
                break
            cur = cur.parent

        raise FileNotFoundError(f"Could not find {cls.SETUP_FILE} starting from {path_package}")


if __name__ == "__main__":
    paths = PackagePaths()
    paths
