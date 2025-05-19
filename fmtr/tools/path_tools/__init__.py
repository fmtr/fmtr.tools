from fmtr.tools.import_tools import MissingExtraMockModule
from fmtr.tools.path_tools.base import Path, PackagePaths

try:
    from fmtr.tools.path_tools.app import AppPaths
except ImportError as exception:
    AppPaths = MissingExtraMockModule('path.app', exception)
