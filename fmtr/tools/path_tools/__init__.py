from fmtr.tools.import_tools import MissingExtraMockModule
from fmtr.tools.path_tools.path_tools import Path, PackagePaths

try:
    from fmtr.tools.path_tools.app_path_tools import AppPaths
except ImportError as exception:
    AppPaths = MissingExtraMockModule('path.app', exception)

try:
    from fmtr.tools.path_tools.type_path_tools import guess
except ImportError as exception:
    guess = MissingExtraMockModule('path.type', exception)
