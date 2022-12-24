from datetime import timedelta
from enum import Enum
from typing import Dict, List, Optional

from pydantic import AnyUrl, BaseModel, Extra, SecretStr

from auth.models.group import Group
from auth.models.user import User
from storage.models.objects import TypeDetection


class Cluster(BaseModel):
    name: str = "ObjectStash-Cluster"
    port: int = 9091
    version: str = "0.0.1"
    initial_peers: List[AnyUrl] = []
    user: User = User()
    group: Group = Group()


class Locking(BaseModel):
    duration: timedelta = timedelta(minutes=5)
    grace: timedelta = timedelta(minutes=1)


# class Timeouts(BaseModel):
#     storage: Lock = Lock()
#     object: Lock = Lock()
#     action: Lock = Lock()


# class Locking(BaseModel):
#     duration: timedelta = timedelta(minutes=1)
#     filename: str = ".lock"


class StorageConfig(BaseModel):
    container: str = "ObjectStash"
    region: Optional[str] = None
    secure: bool = True
    access_key: Optional[SecretStr] = None
    secret_key: Optional[SecretStr] = None


class BasicFormat(BaseModel):
    class Config:
        extra: Extra = Extra.allow


class FormatCSV(BasicFormat):
    separator: str = ","


class FormatXML(BasicFormat):
    pass


class FormatYAML(BasicFormat):
    pass


# Passed to json.dumps as kwargs
class FormatJSON(BasicFormat):
    indent: int = 4  # spaces
    sort_keys: bool = True


class Encoding(BaseModel):
    encoding: str = "utf-8"


class Formatting(BaseModel):
    CSV: FormatCSV = FormatCSV()
    XML: FormatXML = FormatXML()
    YAML: FormatYAML = FormatYAML()
    JSON: FormatJSON = FormatJSON()


class Objects(BaseModel):
    mime_method: TypeDetection = TypeDetection.magic


class Config(BaseModel):
    cluster: Cluster = Cluster()
    storage: Dict[str, StorageConfig] = {"Local": StorageConfig()}
    objects: Objects = Objects()
    encoding: Encoding = Encoding()
    formatting: Formatting = Formatting()
    locking: Locking = Locking()
