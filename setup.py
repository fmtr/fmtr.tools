from fmtr.tools import Setup

DEPENDENCIES = {
    'dev': ['logging', 'version.dev', 'debug', 'sets', 'yaml', 'db.document'],

    'install': [],
    'test': ['pytest-cov'],
    'yaml': ['yamlscript', 'pyyaml'],
    'logging': ['logfire', 'version'],
    'parallel': ['dask[bag]', 'distributed', 'bokeh'],
    'tokenization': ['tokenizers'],
    'augmentation': ['faker', 'sre_yield'],
    'process': ['logging'],
    'profiling': ['contexttimer'],
    'docker.client': ['python-on-whales'],
    'unicode': ['Unidecode'],
    'version': [],
    'version.dev': ['semver'],
    'spaces': ['netrc'],
    'netrc': ['tinynetrc'],
    'hfh': ['huggingface_hub'],
    'merging': ['deepmerge'],
    'api': ['fastapi', 'uvicorn[standard]', 'logging', 'dm', 'logfire[fastapi]'],
    'ai': ['peft', 'transformers[sentencepiece]', 'torchvision', 'torchaudio', 'dm'],
    'dm': ['pydantic', 'pydantic-extra-types', 'pycountry'],
    'openai.api': ['openai'],
    'ai.client': ['logging', 'dm', 'openai.api', 'pydantic-ai[logfire,openai]', 'ollama'],
    'json-fix': ['json_repair'],
    'semantic': ['sentence_transformers', 'metric'],
    'metric': ['tabular'],
    'tabular': ['pandas', 'tabulate', 'openpyxl', 'odfpy', 'deepdiff'],
    'html': ['html2text'],
    'interface': ['flet[all]', 'flet-video', 'flet-webview'],
    'google.api': ['google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client'],
    'caching': ['diskcache', 'cachetools'],
    'pdf': ['pymupdf', 'dm', 'pymupdf4llm'],
    'debug': ['pydevd-pycharm~=251.25410.159'],
    'sets': ['pydantic-settings', 'dm', 'yaml'],
    'path.app': ['appdirs'],
    'path.type': ['filetype'],
    'dns': ['dnspython[doh]', 'http'],
    'patterns': ['regex'],
    'http': ['httpx', 'httpx_retries', 'logging', 'logfire[httpx]'],
    'setup': ['setuptools'],
    'webhook': ['http'],
    'browsers': ['playwright'],
    'db': [],
    'db.document': ['beanie[odm]'],
    'mqtt': ['aiomqtt']

}

setup = Setup(
    dependencies=DEPENDENCIES,
    description='Collection of high-level tools to simplify everyday development tasks, with a focus on AI/ML',
)

setup
