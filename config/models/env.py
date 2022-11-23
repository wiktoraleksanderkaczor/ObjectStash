from datetime import timedelta
from typing import Dict, List

from pydantic import AnyUrl, BaseModel, Extra, SecretStr


class Cluster(BaseModel):
    name: str = "ObjectStash-Cluster"
    port: int = 9091
    initial_peers: List[AnyUrl] = []


class Timeouts(BaseModel):
    lock: timedelta = timedelta(minutes=1)
    action: timedelta = timedelta(minutes=1)


class Storage(BaseModel):
    container: str = "ObjectStash"
    timeouts: Timeouts = Timeouts()
    access_key: SecretStr = ""
    secret_key: SecretStr = ""


class Activity(BaseModel):
    timeouts: Dict[str, int] = Timeouts()


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
    storage: Dict[str, Storage] = {"Local": Storage()}
    activity: Activity = Activity()
    encoding: str = "utf-8"
    formatting: Formatting = Formatting()


def make_config(fname=".objectstash", ext="json"):
    fname = f"{fname}.{ext}"
    config = Config()
    indent = FormatJSON().indent
    with open(fname, "w+") as handle:
        _json = config.json(indent=indent)
        handle.write(_json)


def make_jsonschema(fname=".objectstash", ext="schema.json"):
    fname = f"{fname}.{ext}"
    config = Config()
    indent = FormatJSON().indent
    with open(fname, "w+") as handle:
        _jsonschema = config.schema_json(indent=indent)
        handle.write(_jsonschema)


if __name__ == "__main__":
    make_config()
    make_jsonschema()
