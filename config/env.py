"""Environment configuration."""
import os
from pprint import pprint

from pydantic import ValidationError

from config.constants import CONFIG_FNAME
from config.models.env import Config, FormatJSON


def make_config(fname=CONFIG_FNAME, ext="json") -> Config:
    fname = f"{fname}.{ext}"
    config = Config()
    with open(fname, "w+", encoding="utf-8") as handle:
        _json = config.json(**FormatJSON().dict())
        handle.write(_json)
    return config


def make_jsonschema(fname=CONFIG_FNAME, ext="schema.json"):
    fname = f"{fname}.{ext}"
    config = Config()
    with open(fname, "w+", encoding="utf-8") as handle:
        _jsonschema = config.schema_json(**FormatJSON().dict())
        handle.write(_jsonschema)


def load_config(fname=CONFIG_FNAME) -> Config:
    fname = os.environ.get("OBJECTSTASH_CONFIG_PATH", fname)

    _env: Config
    if os.path.isfile(fname):
        try:
            _env = Config.parse_file(fname)
        except ValidationError as e:
            raise Exception(f"Invalid configuration: {e}") from e
        except Exception as e:
            raise Exception(f"Configuration error: {e}") from e
    else:
        _env = make_config(fname)
    return _env


env: Config = load_config()

if __name__ == "__main__":
    pprint(env.dict())
