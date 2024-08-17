import time

import argparse
import huggingface_hub
import json
import os
from pathlib import Path

FUNCTIONS = [huggingface_hub.snapshot_download]
FUNCTIONS = {func.__name__: func for func in FUNCTIONS}
RETRY_DELAY = 30


def set_token(token):
    token_path = Path(token)
    if token_path.is_file():
        os.environ['HF_TOKEN'] = token_path.read_text().strip()
    else:
        os.environ['HF_TOKEN'] = token


def load_config(path):
    data = Path(path).read_text()
    data = json.loads(data)
    return data


def do_cache(data):
    for datum in data:
        repo_id = datum['repo_id']
        revision = datum.get('revision', 'main')
        print(f'Caching "{repo_id}" [{revision}]...')
        function = FUNCTIONS[datum.pop('function')]

        while True:
            try:
                path = function(**datum)
                print(f'Cached to "{path}".')
                break
            except Exception as exception:
                print(f'Error caching "{repo_id}": {repr(exception)}. Will retry in {RETRY_DELAY} seconds...')
                time.sleep(RETRY_DELAY)


def run(path_config):
    data = load_config(path_config)
    do_cache(data)


def main():
    parser = argparse.ArgumentParser(description="Cache AI artifacts")
    parser.add_argument('--config', help='Path of config file', required=True)
    parser.add_argument('--token', help='Token for HuggingFace API (can be a path or a string)')

    args = parser.parse_args()

    if args.token:
        set_token(args.token)

    run(args.config)


def tag_model(repo_id: str, tag: str):
    """

    Tag a model repository

    """
    api = huggingface_hub.HfApi()
    return api.create_tag(repo_id, tag=tag, repo_type='model')
