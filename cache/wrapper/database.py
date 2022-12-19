from typing import List

from cache.models.replacement import Replacement
from cache.models.wrapper import CacheWrapper
from database.models.database import Database as Wrapped
from database.models.objects import JSON
from storage.models.client import StorageClient
from storage.models.objects import ObjectID


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Database(CacheWrapper, Wrapped):
    def __init__(self, wrapped: Wrapped, storage: StorageClient, replacement: Replacement):
        super().__init__(wrapped, storage, replacement)

    def get(self, key: ObjectID) -> JSON:
        ...

    def exists(self, key: ObjectID) -> bool:
        ...

    def items(self) -> List[ObjectID]:
        ...
