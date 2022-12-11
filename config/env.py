import os
from pprint import pprint

from pydantic import ValidationError

from config.constants import CONFIG_FNAME
from config.logger import log
from config.models.env import Config, make_config

env: Config = None


def load_config(fname=CONFIG_FNAME) -> Config:
    fname = os.environ.get("OBJECTSTASH_CONFIG_PATH", fname)
    fname = f"{fname}.json"

    if os.path.isfile(fname):
        try:
            env = Config.parse_file(fname)
        except ValidationError as e:
            log.error(f"Invalid configuration: {e}")
        except Exception as e:
            log.error(f"Configuration error: {e}")
    else:
        make_config(fname)
        env = Config()
    return env


if __name__ == "__main__":
    config = load_config()
    pprint(config.dict())
