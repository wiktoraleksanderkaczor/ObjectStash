from typing import List, Union

from cache.models.replacement import Replacement
from cache.models.wrapper import CacheWrapper
from storage.models.client.model import StorageClient
from storage.models.client.model import StorageClient as Wrapped
from storage.models.item.data import ObjectData
from storage.models.item.models import Directory, Object
from storage.models.item.paths import DirectoryKey, ObjectKey, StorageKey


class Storage(CacheWrapper, Wrapped):
    def __init__(self, wrapped: Wrapped, storage: StorageClient, replacement: Replacement):
        super().__init__(wrapped, storage, replacement)

    def get(self, key: ObjectKey) -> ObjectData:
        return super().get(key)

    def stat(self, key: StorageKey) -> Union[Object, Directory]:
        return super().stat(key)

    def list(self, prefix: DirectoryKey, recursive: bool = False) -> List[ObjectKey]:
        return super().list(prefix, recursive)

    def exists(self, key: StorageKey) -> bool:
        return super().exists(key)
