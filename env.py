import os
from collections.abc import Mapping
from pprint import pprint
from typing import IO, Any, Dict, List

import pkg_resources
from yaml import load  # ,dump

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def load_env() -> Dict[str, Any]:
    stream: IO[bytes] = pkg_resources.resource_stream(__name__, "default_params.yaml")
    defaults: Dict[str, Any] = load(stream, Loader)
    env_file = "environment.yaml"
    env: Dict[str, Any] = {}
    if os.path.isfile(env_file):
        with open(env_file, "r") as infile:
            env = load(infile, Loader)
            env = nested_update(defaults, env)
    return env


def nested_update(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    for key, val in source.items():
        if isinstance(val, Mapping):
            target[key] = nested_update(target.get(key, {}), val)
        else:
            target[key] = val
    return target


env: Dict[str, Any] = load_env()
container_name: str = env["STORAGE"]["CONTAINER_NAME"]


if __name__ == "__main__":
    pprint(env)
