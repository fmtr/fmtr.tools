import pydevd_pycharm

from fmtr.tools import environment_tools
from fmtr.tools.config import ToolsConfig


def trace(host=environment_tools.get(ToolsConfig.FMTR_DEBUG_HOST_KEY, ToolsConfig.FMTR_DEBUG_HOST), **kwargs):
    """

    Connect to PyCharm debugger

    """
    pydevd_pycharm.settrace(host, port=5679, stdoutToServer=True, stderrToServer=True)
