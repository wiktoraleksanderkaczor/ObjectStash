"""Memory client for storage."""
from typing import Dict, List, Tuple

from config.models.env import StorageConfig
from storage.models.client.medium import Medium
from storage.models.object.file.info import FileData
from storage.models.object.metadata import Metadata
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.superclass.client import BaseStorageClient


class MemoryClient(BaseStorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.storage: Dict[StorageKey, Tuple[Object, FileData]] = {}

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> FileData:
        return self.storage[key][1]

    def stat(self, key: StorageKey) -> Object:
        return self.storage[key][0]

    def put(self, obj: Object, data: FileData) -> None:
        self.storage[obj.name] = (obj, data)

    def remove(self, key: StorageKey) -> None:
        self.storage.pop(key)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        prefixed = [key for key in self.storage if str(key).startswith(str(prefix.path))]
        if not recursive:
            return [key for key in prefixed if key.path.parent == prefix.path]
        return prefixed

    def change(self, key: StorageKey, metadata: Metadata) -> None:
        obj = self.storage[key][0]
        obj.metadata = metadata
        self.storage[key] = (obj, self.storage[key][1])
