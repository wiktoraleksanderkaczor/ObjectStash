"""
This module contains the implementation of an overlay wrapper for the storage client.
"""
from typing import List

from pysyncobj import SyncObjConsumer

from storage.interface.client import StorageClientInterface
from storage.models.object.file.info import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class OverlayWrapper(StorageWrapper):
    def __init__(
        self,
        wrapped: StorageClientInterface,
        overlay: StorageClientInterface,
        consumers: List[SyncObjConsumer],
        symmetric: bool = False,
    ):
        super().__init__(wrapped, consumers)
        self.overlay: StorageClientInterface = overlay
        self.symmetric: bool = symmetric

    def get(self, key: StorageKey) -> FileData:
        if key in self.overlay:
            return self.overlay.get(key)
        if key in self.__wrapped__:
            return self.__wrapped__.get(key)
        raise KeyError(f"Key '{key}' does not exist")

    def stat(self, key: StorageKey) -> Object:
        if key in self.overlay:
            return self.overlay.stat(key)
        if key in self.__wrapped__:
            return self.__wrapped__.stat(key)
        raise KeyError(f"Key '{key}' does not exist")

    def put(self, obj: Object, data: FileData) -> None:
        if self.symmetric:
            self.__wrapped__.put(obj, data)
        return self.overlay.put(obj, data)

    def remove(self, key: StorageKey) -> None:
        if key in self.overlay:
            return self.overlay.remove(key)
        if key in self.__wrapped__:
            return self.__wrapped__.remove(key)
        raise KeyError(f"Key '{key}' does not exist")

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        overlay = self.overlay.list(prefix, recursive=recursive)
        wrapped = self.__wrapped__.list(prefix, recursive=recursive)
        return list(set(overlay + wrapped))

    def __contains__(self, key: StorageKey) -> bool:
        return key in self.overlay or key in self.__wrapped__
