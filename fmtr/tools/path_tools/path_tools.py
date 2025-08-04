import re
import subprocess
from pathlib import Path
from tempfile import gettempdir
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
    def children(self):
        if not self.is_dir():
            return None
        return sorted(self.iterdir(), key=lambda x: x.is_dir(), reverse=True)


class FromCallerMixin:
    """


    """

    def from_caller(self):
        from fmtr.tools.inspection_tools import get_call_path
        path = get_call_path(offset=3).parent
        return path


class PackagePaths(FromCallerMixin):
    """

    Canonical paths for a package.

    """

    dev = Path('/') / 'opt' / 'dev'
    data_global = dev / Constants.DIR_NAME_DATA

    def __init__(self, path=None, org_singleton=None, dir_name_data=Constants.DIR_NAME_DATA, filename_config=Constants.FILENAME_CONFIG, file_version=Constants.FILENAME_VERSION):

        """

        Use calling module path as default path, if not otherwise specified.

        """
        if not path:
            path = self.from_caller()

        self.path = Path(path)
        self.org_singleton = org_singleton
        self.dir_name_data = dir_name_data
        self.filename_config = filename_config
        self.filename_version = file_version

    @property
    def is_dev(self) -> bool:
        """

        Is the package in the dev directory - as opposed to `site-packages` etc?

        """
        return self.path.is_relative_to(self.dev)

    @property
    def is_namespace(self) -> bool:
        """

        If organization is not hard-specified, then the package is a namespace.

        """
        return not bool(self.org_singleton)

    @property
    def name(self) -> str:
        """

        Name of package.

        """
        return self.path.stem

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
    def org(self) -> str:
        """

        Name of organization.

        """
        if not self.is_namespace:
            return self.org_singleton
        else:
            return self.path.parent.stem

    @property
    def repo(self) -> Path:
        """

        Path of repo (i.e. parent of package base directory).

        """
        if self.is_namespace:
            return self.path.parent.parent
        else:
            return self.path.parent

    @property
    def version(self) -> Path:
        """

        Path of version file.

        """
        return self.path / self.filename_version

    @property
    def data(self) -> Path:
        """

        Path of project-specific data directory.

        """

        return self.dev / Constants.DIR_NAME_REPO / self.name_ns / self.dir_name_data

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
        return self.data / self.filename_config

    @property
    def hf(self) -> Path:
        """

        Path of HuggingFace directory

        """
        return self.artifact / Constants.DIR_NAME_HF

    def __repr__(self) -> str:
        """

        Show base path in repr.

        """
        return f'{self.__class__.__name__}("{self.path}")'


if __name__ == "__main__":
    path = Path('/usr/bin/bash').absolute()
    path.type
    path