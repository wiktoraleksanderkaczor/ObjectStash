"""Database model for the database service."""
from pathlib import PurePosixPath
from typing import Callable, List

from database.models.objects import JSON
from storage.interface.client import StorageClientInterface
from storage.interface.path import DirectoryKey, ObjectKey, StorageKey
from storage.models.item.content import ObjectContentInfo, ObjectData
from storage.models.item.models import Object


class Database:
    def insert(self, key: ObjectKey, value: JSON) -> None:
        key = ObjectKey(self.storage.name, self.prefix.path.joinpath(key.path))
        # obj = Object.from_basemodel(name, value)
        data = ObjectData(__root__=value.to_bytes())
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=key, content=content)
        self.storage.put(obj, data)

    def get(self, key: ObjectKey) -> JSON:
        key = ObjectKey(self.storage.name, self.prefix.path.joinpath(key.path))
        if not self.exists(key):
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(key).__root__
        return JSON.parse_raw(data)

    def exists(self, key: StorageKey) -> bool:
        key = StorageKey(self.storage.name, self.prefix.path.joinpath(key.path))
        return self.storage.exists(key)

    def delete(self, key: StorageKey) -> None:
        key = StorageKey(self.storage.name, self.prefix.path.joinpath(key.path))
        if self.exists(key):
            self.storage.remove(key)

    def items(self) -> List[ObjectKey]:
        return self.storage.list(self.prefix)

    def select(self, selector: Callable[[JSON], bool]) -> List[JSON]:
        records = []
        for key in self.items():
            record = self.get(key)
            if selector(record):
                records.append(record)
        return records

    def merge(self, key: ObjectKey, head: JSON) -> None:
        name = ObjectKey(self.storage.name, self.prefix.path.joinpath(key.path))
        base = self.get(name)
        new = JSON.merge(base, head)
        self.insert(key, new)

    def __init__(self, storage: StorageClientInterface, name: DirectoryKey):
        path = PurePosixPath(f"partitions/{name}")
        self.prefix: DirectoryKey = DirectoryKey(storage.name, path)
        self.storage: StorageClientInterface = storage
        # self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")
