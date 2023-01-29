"""Database cache wrapper superclass."""
from typing import List

from cache.interface.replacement import ReplacementInterface
from cache.superclass.wrapper import BaseCacheWrapper
from database.models.database import Database as Wrapped
from database.models.objects import JSON
from storage.interface.client import StorageClientInterface
from storage.interface.path import ObjectKey


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Database(BaseCacheWrapper):
    def __init__(self, wrapped: Wrapped, storage: StorageClientInterface, replacement: ReplacementInterface):
        BaseCacheWrapper.__init__(self, wrapped, storage, replacement)
        self.wrapped: Wrapped = wrapped

    def get(self, _key: ObjectKey) -> JSON:
        ...

    def exists(self, _key: ObjectKey) -> bool:
        ...

    def items(self) -> List[ObjectKey]:
        ...
