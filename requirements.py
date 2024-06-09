from itertools import chain
from typing import List, Dict

from setuptools import find_namespace_packages, setup

INSTALL=[]

DEPENDENCIES = {
    'test': ['pytest-cov'],
    'yaml': ['pyyaml'],
    'logging': ['loguru'],
}


def resolve_values(values) -> List[str]:
    """

    Flatten a list of values.

    """
    values_resolved = []
    for value in values:
        if value not in DEPENDENCIES:
            values_resolved.append(value)
        else:
            values_resolved += resolve_values(DEPENDENCIES[value])
    return values_resolved


def resolve() -> Dict[str, List[str]]:
    """

    Flatten dependencies.

    """
    resolved = {key: resolve_values(values) for key, values in DEPENDENCIES.items()}
    resolved['test'] = list(set(chain.from_iterable(resolved.values())))
    return resolved

EXTRAS=resolve()


if __name__=='__main__':
    import sys
    reqs = []
    reqs += INSTALL
    if len(sys.argv)>1:
        for extra in sys.argv[1].split(','):
            reqs+=EXTRAS[extra]
    reqs='\n'.join(reqs)
    print(reqs)
    reqs