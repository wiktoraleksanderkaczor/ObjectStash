from typing import List

from cache.models.cache import Cache
from cache.models.replacement import Replacement
from database.models.database import Database as Wrapped
from database.models.objects import JSONish
from storage.models.client import StorageClient
from storage.models.objects import ObjectID


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Database(Cache, Wrapped):
    def __init__(self, wrapped: Wrapped, storage: StorageClient, replacement: Replacement):
        super().__init__(wrapped, storage, replacement)

    def get(self, key: ObjectID) -> JSONish:
        ...

    def exists(self, key: ObjectID) -> bool:
        ...

    def items(self) -> List[ObjectID]:
        ...
