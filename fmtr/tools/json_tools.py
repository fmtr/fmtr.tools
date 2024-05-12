import json

from fmtr.tools.config import ToolsConfig


def to_json(obj):
    """

    Serialise to JSON

    """
    json_str = json.dumps(obj, indent=ToolsConfig.SERIALIZATION_INDENT, ensure_ascii=False)
    return json_str


def from_json(json_str: str):
    """

    Deserialise from JSON

    """
    obj = json.loads(json_str)
    return obj
