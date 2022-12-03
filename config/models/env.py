from datetime import timedelta
from typing import Dict, List

from pydantic import AnyUrl, BaseModel, Extra, SecretStr
from strategy import Fail, FailureStrategy

from config.constants import CONFIG_FNAME


class Cluster(BaseModel):
    name: str = "ObjectStash-Cluster"
    port: int = 9091
    initial_peers: List[AnyUrl] = []


class Lock(BaseModel):
    duration: timedelta = timedelta(minutes=1)
    timeout: timedelta = timedelta(minutes=1)
    on_fail: FailureStrategy = Fail()


class Timeouts(BaseModel):
    storage: Lock = Lock()
    object: Lock = Lock()
    action: Lock = Lock()


class Locking(BaseModel):
    duration: timedelta = timedelta(minutes=1)


class StorageConfig(BaseModel):
    container: str = "ObjectStash"
    region: str = ""
    secure: bool = True
    timeouts: Timeouts = Timeouts()
    locking: Locking = Locking()
    access_key: SecretStr = ""
    secret_key: SecretStr = ""


class Defaults(BaseModel):
    timeouts: Timeouts = Timeouts()
    locking: Locking = Locking()


class BasicFormat(BaseModel):
    encoding: str = "utf-8"
    indent: int = 4  # spaces

    class Config:
        extra: Extra = Extra.allow


class FormatCSV(BasicFormat):
    separator: str = ","


class FormatXML(BasicFormat):
    pass


class FormatYAML(BasicFormat):
    pass


class FormatJSON(BasicFormat):
    pass


class Formatting(BaseModel):
    CSV: FormatCSV = FormatCSV()
    XML: FormatXML = FormatXML()
    YAML: FormatYAML = FormatYAML()
    JSON: FormatJSON = FormatJSON()


class Config(BaseModel):
    cluster: Cluster = Cluster()
    storage: Dict[str, StorageConfig] = {"Local": StorageConfig()}
    defaults: Defaults = Defaults()
    encoding: str = "utf-8"
    formatting: Formatting = Formatting()


def make_config(fname=CONFIG_FNAME, ext="json"):
    fname = f"{fname}.{ext}"
    config = Config()
    indent = FormatJSON().indent
    with open(fname, "w+") as handle:
        _json = config.json(indent=indent)
        handle.write(_json)


def make_jsonschema(fname=CONFIG_FNAME, ext="schema.json"):
    fname = f"{fname}.{ext}"
    config = Config()
    indent = FormatJSON().indent
    with open(fname, "w+") as handle:
        _jsonschema = config.schema_json(indent=indent)
        handle.write(_jsonschema)


if __name__ == "__main__":
    make_config()
    make_jsonschema()
