from pathlib import PurePosixPath
from typing import Callable, List

from database.models.objects import JSON
from storage.models.client.model import StorageClient
from storage.models.item.content import ObjectContentInfo
from storage.models.item.data import ObjectData
from storage.models.item.models import Object
from storage.models.item.paths import DirectoryPath, ObjectPath, StorageKey


class Database:
    def insert(self, key: ObjectPath, value: JSON) -> None:
        name = ObjectPath(self.storage.name, self.prefix.joinpath(key))
        # obj = Object.from_basemodel(name, value)
        data = ObjectData(__root__=value.to_bytes())
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=name, content=content)
        self.storage.put(obj, data)

    def get(self, key: ObjectPath) -> JSON:
        name = ObjectPath(self.storage.name, self.prefix.joinpath(key))
        if not self.exists(key):
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(name).__root__
        return JSON.parse_raw(data)

    def exists(self, key: StorageKey) -> bool:
        key = self.prefix.joinpath(key)
        return self.storage.exists(key)

    def delete(self, key: StorageKey) -> None:
        key = self.prefix / key
        if self.exists(key):
            self.storage.remove(key)

    def items(self) -> List[ObjectPath]:
        return self.storage.list(self.prefix)

    def select(self, filter: Callable[[JSON], bool]) -> List[JSON]:
        records = []
        for key in self.items():
            record = self.get(key)
            if filter(record):
                records.append(record)
        return records

    def merge(self, key: ObjectPath, head: JSON) -> None:
        name = ObjectPath(self.storage.name, self.prefix.joinpath(key))
        base = self.get(name)
        new = JSON.merge(base, head)
        self.insert(key, new)

    def __init__(self, storage: StorageClient, name: DirectoryPath):
        self.prefix: DirectoryPath = DirectoryPath(storage.name, PurePosixPath("partitions/")).joinpath(name)
        self.storage: StorageClient = storage
        # self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")
