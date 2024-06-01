import contextlib
import multiprocessing
import random
from functools import lru_cache
from os import getpid
from random import choices, seed

import math


@contextlib.contextmanager
def temporary_seed(seed=0):
    import random
    state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(state)


def choices_w(*data, k=1):
    population, weights = list(zip(*data))
    return choices(population, weights, k=k)


def choice_w(*data):
    return choices_w(*data, k=1)[0]


@lru_cache
def set_seed_mp_pid():
    if multiprocessing.parent_process():
        seed(getpid())


def prob(p=0.5):
    return random.random() <= float(p)


def rand_log10(lower, upper):
    if lower == upper:
        return lower

    is_int = isinstance(lower, int) and isinstance(upper, int)

    if lower < 0 or upper < 0:
        raise ValueError('Only positives are implemented.')

    lower_shift = max(1 - lower, 0)
    upper_shift = max(1 - upper, 0) + lower_shift
    lower_shifted = lower + lower_shift
    upper_shifted = upper + upper_shift

    lower10 = math.log10(lower_shifted)
    upper10 = math.log10(upper_shifted)

    rand10 = random.uniform(lower10, upper10)
    number = 10 ** rand10
    number -= lower_shift

    if is_int:
        number = round(number)

    # TODO Add unit tests:
    # if lower10<upper10:
    #     if rand_lin < lower:
    #         raise ValueError('Return value outside bounds (too small).')
    #     if rand_lin < lower or rand_lin > upper:
    #         raise ValueError('Return value outside bounds (too large).')

    return number
