"""Database model for the database service."""
import pickle
from typing import Any, Callable, List

from database.interface.database import DatabaseInterface
from database.models.objects import JSON
from storage.interface.client import StorageClientInterface
from storage.models.object.content import ObjectContentInfo, ObjectData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath


class BaseDatabase(DatabaseInterface):
    def __contains__(self, key: str) -> bool:
        path = self.prefix.join(key)
        return path in self.storage

    def delete(self, key: str) -> None:
        path = self.prefix.join(key)
        if key in self:
            self.storage.remove(path)

    def items(self) -> List[str]:
        return [item.path.name for item in self.storage.list(self.prefix)]

    def select(self, condition: Callable[[JSON], bool]) -> List[Any]:
        records = []
        for key in self.items():
            record = self.get(key)
            if condition(record):
                records.append(record)
        return records

    def __init__(self, storage: StorageClientInterface, name: StorageKey):
        self.prefix: StorageKey = StorageKey(storage=storage.name, path=StoragePath(f"partitions/{name.path}"))
        self.storage: StorageClientInterface = storage
        # self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")


class DocumentDatabase(BaseDatabase):
    def insert(self, key: str, value: JSON) -> None:
        path = self.prefix.join(key)
        json = value.json()
        encoded = json.encode("utf-8")
        data = ObjectData(__root__=encoded)
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=path, content=content)
        self.storage.put(obj, data)

    def get(self, key: str) -> JSON:
        path = self.prefix.join(key)
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(path).__root__
        return JSON.parse_raw(data)

    def merge(self, key: str, head: JSON) -> None:
        base = self.get(key)
        _, new = JSON.merge(base, head)
        self.insert(key, new)

    def select(self, condition: Callable[[JSON], bool]) -> List[JSON]:
        return super().select(condition)


class ObjectDatabase(BaseDatabase):
    def insert(self, key: str, value: object) -> None:
        path = self.prefix.join(key)
        encoded = pickle.dumps(value)
        data = ObjectData(__root__=encoded)
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=path, content=content)
        self.storage.put(obj, data)

    def get(self, key: str) -> object:
        path = self.prefix.join(key)
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(path).__root__
        return pickle.loads(data)
