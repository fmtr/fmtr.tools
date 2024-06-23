from zlib import crc32

from fmtr.tools.config import ToolsConfig


def hash_unit(value: str) -> float:
    """

    Hash the input string to a value between 0.0 and 1.0 (not secure).

    """
    value = str(value).encode(ToolsConfig.ENCODING)
    return float(crc32(value) & 0xffffffff) / 2 ** 32
