from itertools import chain

from typing import List, Dict

INSTALL=[]

DEPENDENCIES = {
    'test': ['pytest-cov'],
    'yaml': ['pyyaml'],
    'logging': ['loguru'],
    'parallel': ['dask[bag]', 'distributed', 'bokeh'],
    'tokenization': ['tokenizers'],
    'augmentation': ['faker', 'sre_yield'],
    'process': ['logging'],
    'profiling': ['contexttimer'],
    'docker.api': ['docker'],
    'unicode': ['Unidecode'],
    'version': ['semver'],
    'spaces': ['netrc'],
    'netrc': ['tinynetrc'],
    'hfh': ['huggingface_hub'],
    'merging': ['deepmerge'],
    'api': ['fastapi', 'uvicorn', 'logging', 'dm'],
    'ai': ['peft', 'transformers[sentencepiece]', 'torchvision', 'torchaudio', 'dm'],
    'dm': ['pydantic'],
    'json-fix': ['json_repair'],
    'semantic': ['sentence_transformers', 'pandas'],
    'metric': ['pandas'],
    'html': ['html2text'],
    'interface': ['streamlit', 'dm'],
    'openai.api': ['openai'],
    'google.api': ['google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client']
}

CONSOLE_SCRIPTS = [
    'cache-hfh = fmtr.tools.console_script_tools:cache_hfh',
]


def resolve_values(values) -> List[str]:
    """

    Flatten a list of values.

    """
    values_resolved = []
    for value in values:
        if value not in DEPENDENCIES:
            values_resolved.append(value)
        else:
            values_resolved += resolve_values(DEPENDENCIES[value])
    return values_resolved


def resolve() -> Dict[str, List[str]]:
    """

    Flatten dependencies.

    """
    resolved = {key: resolve_values(values) for key, values in DEPENDENCIES.items()}
    resolved['test'] = list(set(chain.from_iterable(resolved.values())))
    return resolved

EXTRAS=resolve()


if __name__=='__main__':
    import sys
    reqs = []
    reqs += INSTALL
    if len(sys.argv)>1:
        for extra in sys.argv[1].split(','):
            reqs+=EXTRAS[extra]
    reqs='\n'.join(reqs)
    print(reqs)
    reqs