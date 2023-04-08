"""
This module contains the implementation of an overlay wrapper for the storage client.
"""
from typing import List

from pysyncobj import SyncObjConsumer

from storage.interface.client import StorageClientInterface
from storage.models.object.content import ObjectData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class ReplicationWrapper(StorageWrapper):
    def __init__(
        self,
        wrapped: StorageClientInterface,
        replica: StorageClientInterface,
        consumers: List[SyncObjConsumer],
    ):
        super().__init__(wrapped, consumers)
        self.replica: StorageClientInterface = replica

    def put(self, obj: Object, data: ObjectData) -> None:
        self.__wrapped__.put(obj, data)
        copy_name = StorageKey(storage=self.replica.name, path=obj.name.path)
        copy_obj = Object(name=copy_name, content=obj.content)
        self.replica.put(copy_obj, data)

    def remove(self, key: StorageKey) -> None:
        self.__wrapped__.remove(key)
        self.replica.remove(key)
