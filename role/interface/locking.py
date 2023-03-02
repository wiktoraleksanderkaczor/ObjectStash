"""
This module contains the LockInterface class.
"""
from abc import ABC, abstractmethod
from pathlib import PurePosixPath

from role.models.locking import State
from storage.interface.client import StorageClientInterface
from storage.models.object.models import StorageKey


class LockInterface(ABC):
    @abstractmethod
    def __init__(self, prefix: PurePosixPath, storage: StorageClientInterface):
        self.prefix: PurePosixPath
        self.storage: StorageClientInterface
        self.state: State
        self.path: PurePosixPath
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
