from typing import List

from cache.models.replacement import Replacement
from cache.models.wrapper import CacheWrapper
from database.models.database import Database as Wrapped
from database.models.objects import JSON
from storage.models.client.model import StorageClient
from storage.models.item.data import ObjectData
from storage.models.item.models import Object
from storage.models.item.paths import ObjectPath


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Database(CacheWrapper, Wrapped):
    def __init__(self, wrapped: Wrapped, storage: StorageClient, replacement: Replacement):
        super().__init__(wrapped, storage, replacement)

    def get(self, key: ObjectPath) -> JSON:
        ...

    def exists(self, key: ObjectPath) -> bool:
        ...

    def items(self) -> List[ObjectPath]:
        ...
