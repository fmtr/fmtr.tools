from typing import Any

from distutils.util import strtobool

from fmtr.tools.tools import Raise


class TypeConversionFailed(ValueError):
    """

    Exception to raise for type conversion failure.

    """


def get_failure_message(raw, type_type):
    """

    Create generic type conversion failure message.

    """
    return f'Failed to convert "{raw}" (type: {type(raw)}) to type {type_type}'


def to_bool(raw: Any, default=None) -> bool:
    """

    Convert a value to a Boolean

    """

    try:
        converted = str(raw)
        converted = strtobool(converted)
        converted = bool(converted)
        return converted
    except ValueError as exception:
        if default is Raise:
            msg = get_failure_message(raw, bool)
            raise TypeConversionFailed(msg) from exception
        else:
            return default


def is_none(value: Any) -> bool:
    return value is None
