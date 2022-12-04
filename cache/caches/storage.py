from typing import List

from cache.models.cache import Cache
from cache.models.replacement import Replacement
from storage.models.client import StorageClient
from storage.models.client import StorageClient as Wrapped
from storage.models.objects import Object, ObjectID, ObjectInfo


class Storage(Cache, Wrapped):
    def __init__(self, wrapped: Wrapped, storage: StorageClient, replacement: Replacement):
        super().__init__(wrapped, storage, replacement)

    def container_exists(self) -> bool:
        ...

    def get_object(self, key: ObjectID) -> Object:
        ...

    def stat_object(self, key: ObjectID) -> ObjectInfo:
        ...

    def list_objects(self, prefix: ObjectID, recursive: bool = False) -> List[ObjectID]:
        ...
