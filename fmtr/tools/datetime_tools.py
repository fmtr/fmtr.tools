from datetime import datetime, timezone
from functools import lru_cache


def now() -> datetime:
    """

    Now UTC

    """
    return datetime.now(tz=timezone.utc)


@lru_cache
def min() -> datetime:
    """

    Min UTC

    """
    return now().min


@lru_cache
def max():
    """

    Max UTC

    """
    return now().max
