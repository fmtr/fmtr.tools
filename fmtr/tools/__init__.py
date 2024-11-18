from fmtr.tools import version_tools as version

__version__ = version.read()

import fmtr.tools.config_tools as config
import fmtr.tools.dataclass_tools as dataclass
import fmtr.tools.datatype_tools as datatype
import fmtr.tools.environment_tools as env
import fmtr.tools.environment_tools as environment
import fmtr.tools.function_tools as function
import fmtr.tools.hash_tools as hash
import fmtr.tools.import_tools as import_
import fmtr.tools.iterator_tools as iterator
import fmtr.tools.json_tools as json
import fmtr.tools.path_tools as path
import fmtr.tools.platform_tools as platform
import fmtr.tools.random_tools as random
import fmtr.tools.string_tools as string
import fmtr.tools.name_tools as name
import fmtr.tools.logging_tools as logging
from fmtr.tools.logging_tools import logger

from fmtr.tools.import_tools import MissingExtraMockModule
from fmtr.tools.path_tools import Path

try:
    from fmtr.tools import augmentation_tools as augmentation
except ImportError as exception:
    augmentation = MissingExtraMockModule('augmentation', exception)

try:
    from fmtr.tools import yaml_tools as yaml
except ImportError as exception:
    yaml = MissingExtraMockModule('yaml', exception)

try:
    from fmtr.tools import docker_tools as docker
    from fmtr.tools.docker_tools import Container
except ImportError as exception:
    docker = Container = MissingExtraMockModule('docker.api', exception)

try:
    from fmtr.tools import parallel_tools as parallel
except ImportError as exception:
    parallel = MissingExtraMockModule('parallel', exception)

try:
    from fmtr.tools import profiling_tools as profiling
    from fmtr.tools.profiling_tools import Timer
except ImportError as exception:
    profiling = Timer = MissingExtraMockModule('profiling', exception)

try:
    import fmtr.tools.process_tools as process
    from fmtr.tools.process_tools import ContextProcess
except ImportError as exception:
    process = ContextProcess = MissingExtraMockModule('process', exception)

try:
    from fmtr.tools import tokenization_tools as tokenization
except ImportError as exception:
    tokenization = MissingExtraMockModule('tokenization', exception)

try:
    from fmtr.tools import unicode_tools as unicode
except ImportError as exception:
    unicode = MissingExtraMockModule('unicode', exception)

try:
    from fmtr.tools import netrc_tools as netrc
except ImportError as exception:
    netrc = MissingExtraMockModule('netrc', exception)

try:
    from fmtr.tools import spaces_tools as spaces
except ImportError as exception:
    spaces = MissingExtraMockModule('spaces', exception)

try:
    from fmtr.tools import hfh_tools as hfh
except ImportError as exception:
    hfh = MissingExtraMockModule('hfh', exception)

try:
    from fmtr.tools import merging_tools as merging
    from fmtr.tools.merging_tools import merge
except ImportError as exception:
    merging = merge = MissingExtraMockModule('merging', exception)

try:
    from fmtr.tools import api_tools as api
except ImportError as exception:
    api = MissingExtraMockModule('api', exception)

try:
    from fmtr.tools import ai_tools as ai
except ImportError as exception:
    ai = MissingExtraMockModule('ai', exception)

try:
    from fmtr.tools import data_modelling_tools as dm
except ImportError as exception:
    dm = MissingExtraMockModule('dm', exception)

try:
    from fmtr.tools import json_fix_tools as json_fix
except ImportError as exception:
    json_fix = MissingExtraMockModule('json_fix', exception)

try:
    from fmtr.tools import semantic_tools as semantic
except ImportError as exception:
    semantic = MissingExtraMockModule('semantic', exception)

try:
    from fmtr.tools import metric_tools as metric
except ImportError as exception:
    metric = MissingExtraMockModule('metric', exception)

try:
    from fmtr.tools import html_tools as html
except ImportError as exception:
    html = MissingExtraMockModule('html', exception)

try:
    from fmtr.tools import interface_tools as interface
except ImportError as exception:
    interface = MissingExtraMockModule('interface', exception)

try:
    from fmtr.tools import openai_tools as openai
except ImportError as exception:
    openai = MissingExtraMockModule('openai', exception)


__all__ = [
    'config',
    'dataclass',
    'datatype',
    'environment',
    'env',
    'function',
    'hash',
    'import_',
    'iterator',
    'json',
    'path',
    'Path',
    'platform',
    'process',
    'ContextProcess',
    'random',
    'string',
    'logging',
    'logger',
    'augmentation',
    'docker',
    'Container',
    'parallel',
    'profiling',
    'Timer',
    'tokenization',
    'unicode',
    'version'
]
