from functools import lru_cache

from tinynetrc import Netrc

LOGIN = 'login'
PASSWORD = 'password'


@lru_cache
def get():
    return Netrc()
