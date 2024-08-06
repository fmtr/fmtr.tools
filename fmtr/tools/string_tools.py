from collections import namedtuple

import re
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


def format_data(value, **kwargs):
    """

    Format a complex object

    """
    if isinstance(value, str):
        return value.format(**kwargs)
    elif isinstance(value, dict):
        return {format_data(k, **kwargs): format_data(v, **kwargs) for k, v in value.items()}
    elif isinstance(value, list):
        return [format_data(item, **kwargs) for item in value]
    else:
        return value


WHITESPACE = re.compile('[\s\-_]+')


def sanitize(*strings, sep: str = '-') -> str:
    """

    Replace spaces with URL- and ID-friendly characters, etc.

    """

    strings = [string for string in strings if string]
    string = ' '.join(strings)
    strings = [c.lower() for c in string if c.isalnum() or c in {' '}]
    string = ''.join(strings)
    string = WHITESPACE.sub(sep, string).strip()

    return string
