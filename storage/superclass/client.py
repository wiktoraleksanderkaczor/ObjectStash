"""
Base class for storage clients.
"""
from typing import List

from config.models.env import StorageConfig
from storage.interface.client import StorageClientInterface
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.object import Object, ObjectData
from storage.models.object.path import StorageKey


class BaseStorageClient(StorageClientInterface):
    def __init__(self, config: StorageConfig):
        self.client = None
        self.config = config

    # REQUIRED:

    def get(self, *key: StorageKey) -> ObjectData:
        ...

    def stat(self, *key: StorageKey) -> Object:
        ...

    def put(self, obj: Object, data: ObjectData) -> None:
        ...

    def remove(self, *key: StorageKey) -> None:
        ...

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        ...

    @property
    def name(self) -> StorageClientKey:
        return StorageClientKey(repr(self))

    @property
    def medium(self) -> Medium:
        ...

    def __contains__(self, key: StorageKey) -> bool:
        try:
            self.stat(key)
        except KeyError:
            return False
        return True

    # Hash for ObjectStash client management set replacement
    def __hash__(self):
        return hash(self.name)

    # String representation for pathing
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.config.repository.name}({self.config.repository.uuid})"
