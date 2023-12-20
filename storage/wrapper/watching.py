"""
This module contains the implementation of an overlay wrapper for the storage client.
"""
from typing import Callable, Dict

from storage.interface.client import StorageClientInterface
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class WatchingWrapper(StorageWrapper):
    def __init__(self, wrapped: StorageClientInterface):
        super().__init__(wrapped)
        self.callbacks: Dict[StorageKey, Callable[[StorageKey], None]] = {}

    def watch(self, key: StorageKey, callback: Callable[[StorageKey], None]) -> None:
        self.callbacks[key] = callback

    def put(self, obj: Object, data: FileData) -> None:
        super().put(obj, data)
        if obj.key in self.callbacks:
            self.callbacks[obj.key](obj.key)

    def remove(self, key: StorageKey) -> None:
        super().remove(key)
        if key in self.callbacks:
            self.callbacks[key](key)
