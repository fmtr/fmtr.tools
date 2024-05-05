from typing import Any

from fmtr.tools.config import ToolsConfig


class MissingExtraError(ImportError):
    """

    Error to raise if extras are missing.

    """


def raise_missing_extra(extra, exception, library=ToolsConfig.LIBRARY_NAME):
    """

    Raise if required dependencies are missing.

    """
    msg = f'The current module is missing dependencies. To install them, run: pip install {library}[{extra}] --upgrade'
    raise MissingExtraError(msg) from exception


def identity(x: Any) -> Any:
    """

    Dummy (identity) function

    """
    return x


class Empty:
    """

    Class to denote an unspecified object (e.g. argument) when `None` cannot be used.

    """


class Raise:
    """

    Class to denote when a function should raise instead of e.g. returning a default.

    """


EMPTY = Empty()
