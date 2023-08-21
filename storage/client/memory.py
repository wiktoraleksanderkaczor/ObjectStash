"""Memory client for storage."""
from typing import Dict, Tuple

from storage.models.client.medium import Medium
from storage.models.object.file.info import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.superclass.client import BaseStorageClient


class MemoryClient(BaseStorageClient):
    def __init__(self):
        super().__init__()
        self.storage: Dict[StorageKey, Tuple[Object, FileData]] = {}

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> FileData:
        return self.storage[key][1]

    def put(self, obj: Object, data: FileData) -> None:
        self.storage[obj.key] = (obj, data)

    def remove(self, key: StorageKey) -> None:
        self.storage.pop(key)
