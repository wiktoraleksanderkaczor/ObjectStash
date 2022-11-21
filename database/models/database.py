from typing import Any, Dict, List

from database.locking.database import DatabaseLock
from database.models.locking import Lock
from database.models.objects import JSONish
from storage.client.models.client import StorageClient
from storage.client.models.objects import ObjectID

# from database.merging.merge import _merge_mapping
# from database.merging.models.index import MergeIndex
# from database.merging.models.mode import MergeMode
# from database.merging.models.strategy import MergeStrategy


class Database:
    def insert(self, key: ObjectID, value: JSONish) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.put_object(key, value)

    def get(self, key: ObjectID) -> JSONish:
        key = self.prefix.joinpath(key)
        return self.storage.get_object(key) if self.exists(key) else None

    def exists(self, key: ObjectID) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.object_exists(key)

    def delete(self, key: ObjectID) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.remove_object(key) if self.exists(key) else None

    def items(self) -> List[ObjectID]:
        return self.storage.list_objects(self.prefix)

    def select(filter: Dict[str, Any]) -> List[ObjectID]:
        pass

    # def merge(
    #     self,
    #     key: ObjectID,
    #     data: JSONish,
    #     index: MergeIndex = None,
    #     merge: MergeStrategy = None,
    #     mode: MergeMode = MergeMode.UPDATE,
    # ) -> bool:
    #     key = self.prefix.joinpath(key)
    #     old = self.get(key)
    #     new = _merge_mapping(old, data, index, merge, mode)
    #     return self.insert(key, new)

    def __init__(self, storage: StorageClient, name: ObjectID):
        self.prefix: ObjectID = ObjectID("partitions/").joinpath(name)
        self.storage: StorageClient = storage
        self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")
