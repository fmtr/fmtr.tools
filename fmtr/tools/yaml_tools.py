from typing import Any
from yaml import CLoader as Loader, CDumper as Dumper
from yaml import load, dump


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
