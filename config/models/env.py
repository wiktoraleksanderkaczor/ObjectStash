"""Environment configuration model."""
from datetime import timedelta
from enum import Enum
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, Extra

from auth.models.group import Group
from auth.models.user import User


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
    objects: Objects = Objects()
    locking: Locking = Locking()
