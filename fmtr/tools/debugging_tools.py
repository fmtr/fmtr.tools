import pydevd_pycharm

from fmtr.tools import environment_tools as env
from fmtr.tools.config import ToolsConfig

MASK = 'Starting debugger at tcp://{host}:{port}...'

def trace(is_debug=None, host=None, port=None, stdoutToServer=True, stderrToServer=True, **kwargs):
    """

    Connect to PyCharm debugger if enabled

    """
    if not is_debug:
        is_debug = env.get_bool(ToolsConfig.FMTR_REMOTE_DEBUG_ENABLED_KEY, False)

    if not is_debug:
        return

    if is_debug is True and not host:
        host = ToolsConfig.FMTR_REMOTE_DEBUG_HOST_DEFAULT

    host = host or env.get(ToolsConfig.FMTR_REMOTE_DEBUG_HOST_KEY, ToolsConfig.FMTR_REMOTE_DEBUG_HOST_DEFAULT)
    port = port or ToolsConfig.FMTR_REMOTE_DEBUG_PORT_DEFAULT

    from fmtr.tools import logger

    msg = MASK.format(host=host, port=port)
    logger.info(msg)

    pydevd_pycharm.settrace(host, port=port, stdoutToServer=stdoutToServer, stderrToServer=stderrToServer, **kwargs)
