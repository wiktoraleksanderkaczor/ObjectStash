from abc import ABC, abstractmethod
from pathlib import PurePosixPath

from role.models.locking import State
from storage.interface.client import StorageClient
from storage.models.item.models import ObjectKey


class LockInterface(ABC):
    @abstractmethod
    def __init__(self, prefix: PurePosixPath, storage: StorageClient):
        self.prefix: PurePosixPath
        self.storage: StorageClient
        self.state: State
        self.path: PurePosixPath
        self.key: ObjectKey

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
