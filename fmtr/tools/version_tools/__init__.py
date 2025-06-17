from fmtr.tools.import_tools import MissingExtraMockModule

from fmtr.tools.version_tools.version_tools import read, read_path, get

try:
    import semver

    semver = semver
    parse = semver.VersionInfo.parse

except ImportError as exception:
    semver = parse = MissingExtraMockModule('version.dev', exception)
