from collections import namedtuple

import re
from string import Formatter
from typing import List

from fmtr.tools.datatype_tools import is_none

ELLIPSIS = '…'
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


def truncate_mid(text, length=None, sep=ELLIPSIS):
    """

    Truncate a string to `length` characters in the middle

    """
    text = flatten(text)
    if len(text) <= length or not length:
        return text
    half_length = (length - 3) // 2
    return text[:half_length] + sep + text[-half_length:]


def flatten(raw):
    """

    Flatten a multiline string to a single line

    """
    lines = raw.splitlines()
    text = ' '.join(lines)
    text = text.strip()
    return text


def join(strings, sep=' '):
    """

    Join a list of strings while removing Nones

    """

    lines = [string for string in strings if not is_none(string) and string != '']
    text = sep.join(str(line) for line in lines)
    return text


class Mask:
    """

    Allows partial-like f-strings

    """

    def __init__(self, mask: str):
        self.mask = mask
        self.kwargs = {}
        self.args = []

    def format(self, *args, **kwargs):
        """

        If the string is complete, return it, else store field values

        """
        self.args += list(args)
        self.kwargs.update(kwargs)
        try:
            text = self.mask.format(*args, **self.kwargs)
            return text
        except (KeyError, IndexError):
            return self


if __name__ == '__main__':
    import numpy as np

    st = join([1, None, 'test', np.nan, 0, '', 'yeah'])
    st
