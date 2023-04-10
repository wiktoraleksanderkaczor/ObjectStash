"""Environment configuration model."""
from datetime import timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, Extra, IPvAnyAddress, SecretStr

from auth.models.group import Group
from auth.models.user import User
from storage.models.client.repository import Repository


class Cluster(BaseModel):
    name: str = "Pioneer-Cluster"
    port: int = 9091
    fqdn_service: str = "_pioneer._tcp.local."
    version: str = "0.0.1"
    initial_peers: List[AnyUrl] = []
    user: User = User()
    group: Group = Group()


class StorageLocking(BaseModel):
    duration: timedelta = timedelta(minutes=5)
    grace: timedelta = timedelta(minutes=1)


class ObjectLocking(BaseModel):
    duration: timedelta = timedelta(minutes=5)
    grace: timedelta = timedelta(minutes=1)


class Locking(BaseModel):
    objects: ObjectLocking = ObjectLocking()
    storage: StorageLocking = StorageLocking()


class StorageConfig(BaseModel):
    endpoint: Union[AnyUrl, IPvAnyAddress] = AnyUrl("pioneer://localhost", scheme="pioneer")
    repository: Repository = Repository()
    region: Optional[str] = None
    secure: bool = True
    access_key: Optional[SecretStr] = None
    secret_key: Optional[SecretStr] = None

    class Config:
        extra: Extra = Extra.allow


class SerializationFallback(str, Enum):
    JSONPICKLE = "jsonpickle"


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


class Serialization(BaseModel):
    encoding: Encoding = Encoding()
    formatting: Formatting = Formatting()
    fallback: Optional[SerializationFallback] = None


class Objects(BaseModel):
    pass


class Config(BaseModel):
    cluster: Cluster = Cluster()
    serialization: Serialization = Serialization()
    storage: Dict[str, StorageConfig] = {"Local": StorageConfig()}
    objects: Objects = Objects()
    locking: Locking = Locking()
