from typing import Any

from fmtr.tools.constants import Constants


class MissingExtraError(ImportError):
    """

    Error to raise if extras are missing.

    """

    MASK = 'The current module is missing dependencies. To install them, run: `pip install {library}[{extra}] --upgrade`'

    def __init__(self, extra):
        self.message = self.MASK.format(library=Constants.LIBRARY_NAME, extra=extra)

        super().__init__(self.message)


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
