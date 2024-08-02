from fmtr.tools.import_tools import MissingExtraMockModule
from fmtr.tools.inspection_tools import get_call_path

try:
    import semver

    semver = semver
    parse = semver.VersionInfo.parse
except ImportError as exception:
    parse = MissingExtraMockModule('version', exception)
    semver = MissingExtraMockModule('version', exception)


def read() -> str:
    """

    Read a generic version file from the calling package path. Optionally add dev build info.

    """
    import os
    from fmtr.tools.tools import ToolsConfig
    from fmtr.tools import datatype_tools
    path = get_call_path(offset=2).parent / 'version'
    text = path.read_text(encoding=ToolsConfig.ENCODING).strip()

    is_dev = datatype_tools.to_bool(os.getenv('FMTR_DEV', default=False))

    if is_dev:
        import datetime

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(ToolsConfig.DATETIME_SEMVER_BUILD_FORMAT)

        version = parse(text)
        version = version.bump_patch()
        version = version.replace(prerelease='dev', build=timestamp)
        text = str(version)

    return text
