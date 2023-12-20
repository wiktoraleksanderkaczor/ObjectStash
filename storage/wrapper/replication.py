"""
This module contains the implementation of an overlay wrapper for the storage client.
"""

from storage.interface.client import StorageClientInterface
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class ReplicationWrapper(StorageWrapper):
    def __init__(
        self,
        wrapped: StorageClientInterface,
        replica: StorageClientInterface,
    ):
        super().__init__(wrapped)
        self.replica: StorageClientInterface = replica

    def put(self, obj: Object, data: FileData) -> None:
        self.__wrapped__.put(obj, data)
        copy_name = StorageKey(storage=self.replica.name, path=obj.key.path)
        copy_obj = Object(key=copy_name, metadata=obj.metadata, item=obj.item)
        self.replica.put(copy_obj, data)

    def remove(self, key: StorageKey) -> None:
        self.__wrapped__.remove(key)
        self.replica.remove(key)
