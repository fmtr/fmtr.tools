from itertools import chain
from typing import List, Dict, Any


def enlist(value) -> List[Any]:
    """

    Make a non-list into a singleton list

    """
    enlisted = value if isinstance(value, list) else [value]
    return enlisted


def dict_records_to_lists(data: List[Dict[Any, Any]], missing: Any = None) -> Dict[Any, List[Any]]:
    """

    Convert a list of dictionaries to lists format

    """
    keys = set(chain.from_iterable([datum.keys() for datum in data]))
    as_lists = {key: [] for key in keys}
    for datum in data:
        for key in keys:
            as_lists[key].append(datum.get(key, missing))
    return as_lists


def get_batch_sizes(total, num_batches):
    """

    Calculate the sizes of batches for a given total number of items and number of batches.

    """
    return [total // num_batches + (1 if x < total % num_batches else 0) for x in range(num_batches)]


def chunk_data(data, size: int):
    """

    Chunk data into batches of a given size, plus any remainder

    """
    chunked = [data[offset:offset + size] for offset in range(0, len(data), size)]
    return chunked
