"""
This module contains the LockInterface class.
"""
from abc import ABC, abstractmethod

from role.models.locking import State
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey, StoragePath


class LockInterface(ABC):
    @abstractmethod
    def __init__(self, prefix: StoragePath, storage: StorageClientInterface):
        self.prefix: StoragePath
        self.storage: StorageClientInterface
        self.state: State
        self.path: StoragePath
        self.key: StorageKey

    @abstractmethod
    def acquire(self) -> None:
        ...

    @abstractmethod
    def release(self) -> None:
        ...

    @abstractmethod
    def refresh(self) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> "LockInterface":
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    def __del__(self) -> None:
        ...
