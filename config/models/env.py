from datetime import timedelta
from typing import Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Extra, SecretStr


class Cluster(BaseModel):
    name: str = "ObjectStash-Cluster"
    port: int = 9091
    initial_peers: List[AnyUrl] = []


class Lock(BaseModel):
    duration: timedelta = timedelta(minutes=1)
    timeout: timedelta = timedelta(minutes=1)


class Timeouts(BaseModel):
    storage: Lock = Lock()
    object: Lock = Lock()
    action: Lock = Lock()


class Locking(BaseModel):
    duration: timedelta = timedelta(minutes=1)
    filename: str = ".lock"


class StorageConfig(BaseModel):
    container: str = "ObjectStash"
    region: Optional[str] = None
    secure: bool = True
    timeouts: Timeouts = Timeouts()
    locking: Locking = Locking()
    access_key: Optional[SecretStr] = None
    secret_key: Optional[SecretStr] = None


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
    encoding: str = "utf-8"
    formatting: Formatting = Formatting()
