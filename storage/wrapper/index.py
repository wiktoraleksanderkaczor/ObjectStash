"""
This wrapper creates an index of the wrapped storage.
"""
from typing import List

from database.paradigms.nosql import NoSQL
from datamodel.data.model import Data
from storage.interface.client import StorageClientInterface
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath
from storage.wrapper.interface import StorageWrapper


class IndexWrapper(StorageWrapper):
    def __init__(self, wrapped: StorageClientInterface, storage: StorageClientInterface):
        super().__init__(wrapped)
        self.storage: StorageClientInterface = storage
        root_path = StorageKey(storage=storage.name, path=StoragePath(path=""))

        self.index = NoSQL(f"index/{self.__wrapped__.name}", self.storage)
        for item in self.__wrapped__.list(root_path, recursive=True):
            stat = self.__wrapped__.stat(item)
            self.index.insert(str(item.path), Data.from_obj(stat.to_dict()))

    def put(self, obj: Object, data: FileData) -> None:
        self.__wrapped__.put(obj, data)
        self.index.insert(str(obj.key.path), Data.from_obj(obj.to_dict()))

    def remove(self, key: StorageKey) -> None:
        self.__wrapped__.remove(key)
        self.index.delete(str(key.path))

    def stat(self, key: StorageKey) -> Object:
        data = self.index.get(str(key.path))
        if data is None:
            data = self.__wrapped__.stat(key)
            self.index.insert(str(key.path), Data.from_obj(data.to_dict()))
        data = data.to_dict()
        return Object(**data)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        items = [item for item in self.index.items() if item.startswith(str(prefix.path))]
        if not recursive:
            items = [item for item in items if "/" not in item.replace(str(prefix.path), "")]
        return [StorageKey(storage=self.__wrapped__.name, path=StoragePath(path=item)) for item in items]

    def __contains__(self, key: StorageKey) -> bool:
        if str(key.path) in self.index:
            return True
        if key in self.__wrapped__:
            self.index.insert(str(key.path), Data.from_obj(self.__wrapped__.stat(key).to_dict()))
            return True
        return False
