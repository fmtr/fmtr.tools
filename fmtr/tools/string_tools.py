from collections import namedtuple

from string import Formatter
from typing import List

formatter = Formatter()

Segment = namedtuple('Segment', ['literal_text', 'field_name', 'format_spec', 'conversion'])


def parse_string(string: str) -> List[Segment]:
    """

    Return structured version of a string with formatting slots.

    """
    parsed = [Segment(*args) for args in formatter.parse(string)]
    return parsed


def is_format_string(string: str) -> bool:
    """

    Does the string contains string formatting slots (i.e. {})?

    """
    try:
        parsed = parse_string(string)
    except ValueError:
        return False
    if all(datum.field_name is None for datum in parsed):
        return False
    else:
        return True


def get_var_name(string: str) -> str:
    """

    Get the name of a variable from a (resolved) f-string `{a=}`

    """
    name, value = string.split('=', maxsplit=1)
    return name
