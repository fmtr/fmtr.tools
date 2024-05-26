"""

Tools for handling environment variables etc.

"""
import os
from collections.abc import Callable
from datetime import date, datetime
from typing import Any, Dict

from fmtr.tools.datatype_tools import to_bool
from fmtr.tools.path_tools import Path
from fmtr.tools.tools import identity, EMPTY


class MissingEnvironmentVariable(KeyError):
    """

    Exception for when a required environment variable is missing.

    """


def get_env_dict() -> Dict[str, str]:
    """

    Return environment variables as a standard dictionary.

    """
    environment_dict = dict(os.environ)
    return environment_dict


def get_env(name: str, default: Any = EMPTY, converter: Callable = identity, convert_empty: bool = False) -> Any:
    """

    Return the specified environment variable, handling default substitution and simple type conversion.

    """
    value = os.getenv(name, default)

    if value is EMPTY:
        msg = f'Environment variable "{name}" is required but has not been set'
        raise MissingEnvironmentVariable(msg)

    if value is not None or convert_empty:
        value = converter(value)

    return value


def get_env_getter(converter: Callable) -> Callable:
    """

    Return an environment getter for the specified type.

    """

    def func(name: str, default: Any = EMPTY):
        """

        Environment getter that converts to the specified type

        """
        value = get_env(name, default=default, converter=converter)
        return value

    return func


get_env_int = get_env_getter(lambda n: int(float(n)))
get_env_float = get_env_getter(float)
get_env_bool = get_env_getter(to_bool)
get_env_date = get_env_getter(date.fromisoformat)
get_env_datetime = get_env_getter(datetime.fromisoformat)
get_env_path = get_env_getter(Path)
