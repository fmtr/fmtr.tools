from typing import Any

try:
    from yaml import load, dump
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError as exception:  # pragma: no cover
    from fmtr.tools.tools import raise_missing_extra

    raise_missing_extra('yaml', exception)


def to_yaml(obj: Any) -> str:
    """



    """
    yaml_str = dump(obj, allow_unicode=True, Dumper=Dumper)
    return yaml_str


def from_yaml(yaml_str: str) -> Any:
    """



    """
    obj = load(yaml_str, Loader=Loader)
    return obj
