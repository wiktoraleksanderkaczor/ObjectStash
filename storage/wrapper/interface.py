"""
Interface for storage wrapper.
"""
from typing import List

from pysyncobj import SyncObjConsumer

from role.superclass.wrapping import DistributedObjectProxy
from storage.interface.client import StorageClientInterface
from storage.models.object.file.info import FileData
from storage.models.object.metadata import Metadata
from storage.models.object.models import Object
from storage.models.object.path import StorageKey


class StorageWrapper(DistributedObjectProxy, StorageClientInterface):
    def __init__(self, wrapped: StorageClientInterface, consumers: List[SyncObjConsumer]):
        super().__init__(wrapped, consumers)
        self.__wrapped__: StorageClientInterface = wrapped  # typing fix

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.__wrapped__)})"

    def get(self, key: StorageKey) -> FileData:
        return self.__wrapped__.get(key)

    def stat(self, key: StorageKey) -> Object:
        return self.__wrapped__.stat(key)

    def put(self, obj: Object, data: FileData) -> None:
        return self.__wrapped__.put(obj, data)

    def remove(self, key: StorageKey) -> None:
        return self.__wrapped__.remove(key)

    def change(self, key: StorageKey, metadata: Metadata) -> None:
        return self.__wrapped__.change(key, metadata)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        return self.__wrapped__.list(prefix, recursive)

    def __contains__(self, key: StorageKey) -> bool:
        return key in self.__wrapped__

    @property
    def __dict__(self):
        # Might be needed for more correct behavior later, unknown if properly writable
        # merged = {}
        # merged.update(super().__dict__)
        # merged.update(self.__wrapped__.__dict__)
        return self.__wrapped__.__dict__

    @property
    def name(self) -> str:
        return self.__wrapped__.name

    @property
    def medium(self) -> str:
        return self.__wrapped__.medium
