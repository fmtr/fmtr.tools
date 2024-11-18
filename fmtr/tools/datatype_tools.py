from typing import Any

from fmtr.tools.tools import Raise

TRUES = {str(True).lower(), str(1), 'y', 'yes'}


class TypeConversionFailed(ValueError):
    """

    Exception to raise for type conversion failure.

    """


def get_failure_message(raw, type_type):
    """

    Create generic type conversion failure message.

    """
    return f'Failed to convert "{raw}" (type: {type(raw)}) to type {type_type}'


def is_numeric(value) -> bool:
    """

    Test whether a variable is any numeric type

    """
    import numbers
    return isinstance(value, numbers.Number)


def to_bool(raw: Any, default=None) -> bool:
    """

    Convert a value to a Boolean

    """

    try:
        converted = str(raw).lower()
        converted = converted in TRUES
        return converted
    except ValueError as exception:
        if default is Raise:
            msg = get_failure_message(raw, bool)
            raise TypeConversionFailed(msg) from exception
        else:
            return default


def is_none(value: Any) -> bool:
    return value is None
