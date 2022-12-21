from typing import Callable, List

from database.models.objects import JSON
from storage.models.client import StorageClient
from storage.models.objects import Object, ObjectID


class Database:
    def insert(self, key: ObjectID, value: JSON) -> bool:
        name = str(self.prefix.joinpath(key))
        obj = Object.from_basemodel(name, value)
        return self.storage.put_object(obj)

    def get(self, key: ObjectID) -> JSON:
        key = self.prefix.joinpath(key)
        if not self.exists(key):
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get_object(key).data
        return JSON.parse_raw(data)

    def exists(self, key: ObjectID) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.object_exists(key)

    def delete(self, key: ObjectID) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.remove_object(key) if self.exists(key) else True

    def items(self) -> List[ObjectID]:
        return self.storage.list_objects(self.prefix)

    def select(self, filter: Dict[str, Any]) -> List[ObjectID]:  # type: ignore for now
        pass

    def merge(self, key: ObjectID, head: JSON) -> bool:
        key = self.prefix.joinpath(key)
        base = self.get(key)
        new = JSON.merge(base, head)
        return self.insert(key, new)

    def __init__(self, storage: StorageClient, name: ObjectID):
        self.prefix: ObjectID = ObjectID("partitions/").joinpath(name)
        self.storage: StorageClient = storage
        # self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")
