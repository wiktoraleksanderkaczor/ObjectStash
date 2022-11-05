from enum import Enum
from typing import List

from pydantic import Protocol, SecretStr

from clients.local_client import LocalCLient
from clients.minio_client import MinioClient
from models.objects import Object, ObjectInfo

from ..config.env import env
from .objects import Key


class Capability(str, Enum):
    BASIC = "BASIC"
    STREAMS = "STREAMS"
    INSERT = "INSERT"


# Handling singular and multiple object operations is done by calling the singular function multiple times by default
# If client has appropriate efficient functions, that can be called instead
# At a minimum, to implement the class, one requires;
# - all singular operations
# - all multiple operations without a singular alternative


class StorageClient(Protocol):
    client_name: str
    capabilities: List[Capability]

    def __init__(self, container: str, region: str = None, secure: bool = True):
        self.client = None
        self.container = container
        self.region = region
        self.secure = secure
        self.access_key: SecretStr = env["STORAGE"]["ACCESS_KEY"]
        self.secret_key: SecretStr = env["STORAGE"]["SECRET_KEY"]

    # REQUIRED:

    def container_exists(self) -> bool:
        ...

    def create_container(self) -> bool:
        ...

    def list_objects(self, prefix: Key, recursive: bool = False) -> List[Key]:
        ...

    def get_object(self, key: Key) -> Object:
        ...

    def put_object(self, key: Key, obj: Object) -> bool:
        ...

    def stat_object(self, key: Key) -> ObjectInfo:
        ...

    def remove_object(self, key: Key) -> bool:
        ...

    # OPTIONAL:

    def get_objects(self, keys: List[Key]) -> List[Object]:
        return [self.get_object(key) for key in keys]

    def put_objects(self, keys: List[Key], data: List[Object]) -> List[bool]:
        return [self.put_object(key, item) for key, item in zip(keys, data)]

    def stat_objects(self, keys: List[Key]) -> List[ObjectInfo]:
        return [self.stat_object(key) for key in keys]

    def remove_objects(self, keys: List[Key]) -> List[bool]:
        return [self.remove_object(key) for key in keys]

    def object_exists(self, key: Key) -> bool:
        return key in self.list_objects(key.parent)


STORAGE_CLIENTS = {"Local": LocalCLient, "MinIO": MinioClient}
storage: StorageClient = STORAGE_CLIENTS.get(env["STORAGE"]["CLIENT"], LocalCLient)
