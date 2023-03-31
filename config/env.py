"""Environment configuration."""
import os
from pprint import pprint

from pydantic import ValidationError

from config.constants import CONFIG_PATH, CONFIG_SCHEMA_PATH
from config.models.env import Config, FormatJSON


def make_config(path=CONFIG_PATH) -> Config:
    config = Config()
    with open(path, "w+", encoding="utf-8") as handle:
        _json = config.json(**FormatJSON().dict())
        handle.write(_json)
    return config


def make_jsonschema(path=CONFIG_SCHEMA_PATH):
    config = Config()
    with open(path, "w+", encoding="utf-8") as handle:
        _jsonschema = config.schema_json(**FormatJSON().dict())
        handle.write(_jsonschema)


def load_config(path=CONFIG_PATH) -> Config:
    path = os.environ.get("PIONEER_CONFIG_PATH", path)

    _env: Config
    if os.path.isfile(path):
        try:
            _env = Config.parse_file(path)
        except ValidationError as e:
            raise ValidationError(f"Invalid configuration: {e}", Config) from e
        except Exception as e:
            raise RuntimeError(f"Configuration error: {e}") from e
    else:
        _env = make_config(path)
    return _env


env: Config = load_config()

if __name__ == "__main__":
    pprint(env.dict())
