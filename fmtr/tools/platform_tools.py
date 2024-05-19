import platform
from functools import lru_cache


@lru_cache
def is_wsl():
    """



    """
    uname_data = platform.uname()
    is_wsl = uname_data.system.lower() == 'linux' and 'microsoft' in uname_data.release.lower()
    return is_wsl