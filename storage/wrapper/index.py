"""
This wrapper creates an index of the wrapped storage.
"""
from pathlib import PurePosixPath
from typing import List

from pysyncobj import SyncObjConsumer

from database.models.objects import JSON
from database.paradigms.nosql import NoSQL
from storage.interface.client import StorageClientInterface
from storage.models.object.content import ObjectData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class IndexWrapper(StorageWrapper):
    def __init__(
        self, wrapped: StorageClientInterface, storage: StorageClientInterface, consumers: List[SyncObjConsumer]
    ):
        super().__init__(wrapped, consumers)
        self.storage: StorageClientInterface = storage
        root_path = StorageKey(storage=storage.name, path=PurePosixPath("/"))

        self.index = NoSQL(self.storage, StorageKey(storage=self.storage.name, path=PurePosixPath("index")))
        for item in self.__wrapped__.list(root_path, recursive=True):
            stat = self.__wrapped__.stat(item)
            self.index.insert(str(item.path), JSON(__root__=stat.json()))

    def put(self, obj: Object, data: ObjectData) -> None:
        self.__wrapped__.put(obj, data)
        self.index.insert(str(obj.name.path), JSON(__root__=obj.json()))

    def remove(self, key: StorageKey) -> None:
        self.__wrapped__.remove(key)
        self.index.delete(str(key.path))

    def stat(self, key: StorageKey) -> Object:
        data = self.index.get(str(key.path))
        data = data.dict()
        return Object(**data)

    # TODO: Continue here...
