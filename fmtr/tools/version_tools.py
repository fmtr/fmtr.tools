from fmtr.tools.import_tools import MissingExtraMockModule
from fmtr.tools.inspection_tools import get_call_path

try:
    import semver

    semver = semver
    parse = semver.VersionInfo.parse
except ImportError as exception:
    # Special case to allow module import.
    # Should be slit out into separate version.dev subpackage
    parse = MissingExtraMockModule('version', exception)
    semver = MissingExtraMockModule('version', exception)


def read() -> str:
    """

    Read a generic version file from the calling package path.

    """

    path = get_call_path(offset=2).parent / 'version'
    return read_path(path)


def read_path(path) -> str:
    """

    Read in version from specified path

    """
    from fmtr.tools.tools import Constants
    text = path.read_text(encoding=Constants.ENCODING).strip()

    text = get(text)
    return text


def get(text) -> str:
    """

    Optionally add dev build info to raw version string.

    """
    import os
    from fmtr.tools import datatype_tools

    is_dev = datatype_tools.to_bool(os.getenv('FMTR_DEV', default=False))

    if is_dev:
        import datetime
        from fmtr.tools.tools import Constants

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(Constants.DATETIME_SEMVER_BUILD_FORMAT)

        version = parse(text)
        version = version.bump_patch()
        version = version.replace(prerelease='dev', build=timestamp)
        text = str(version)

    return text
