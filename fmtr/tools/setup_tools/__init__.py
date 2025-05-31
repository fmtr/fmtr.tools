from fmtr.tools.import_tools import MissingExtraMockModule

from fmtr.tools.setup_tools.setup_tools import Setup, SetupPaths, Dependencies, Tools

try:
    from setuptools import find_namespace_packages, find_packages, setup as setup_setuptools
except ImportError as exception:
    find_namespace_packages = find_packages = setup_setuptools = MissingExtraMockModule('setup', exception)
