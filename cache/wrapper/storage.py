"""Storage cache wrapper."""

from typing import List, Union

from cache.interface.replacement import ReplacementInterface
from cache.superclass.wrapper import BaseCacheWrapper
from storage.interface.client import StorageClientInterface as Wrapped
from storage.interface.path import DirectoryKey, ObjectKey, StorageKey
from storage.models.item.content import ObjectData
from storage.models.item.models import Directory, Object


class Storage(BaseCacheWrapper):
    def __init__(self, wrapped: Wrapped, storage: Wrapped, replacement: ReplacementInterface):
        BaseCacheWrapper.__init__(self, wrapped, storage, replacement)
        self.wrapped: Wrapped = wrapped

    def get(self, key: ObjectKey) -> ObjectData:
        return self.wrapped.get(key)

    def stat(self, key: StorageKey) -> Union[Object, Directory]:
        return self.wrapped.stat(key)

    def list(self, prefix: DirectoryKey, recursive: bool = False) -> List[ObjectKey]:
        return self.wrapped.list(prefix, recursive)

    def exists(self, key: StorageKey) -> bool:
        return self.wrapped.exists(key)
