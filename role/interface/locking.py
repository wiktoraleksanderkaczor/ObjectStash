from abc import ABC, abstractmethod
from pathlib import PurePosixPath

from role.models.locking import State
from storage.interface.client import StorageClient
from storage.models.item.models import ObjectKey


class Lock(ABC):
    @abstractmethod
    def __init__(self, prefix: PurePosixPath, storage: StorageClient):
        self.prefix: PurePosixPath
        self.storage: StorageClient
        self.state: State
        self.path: PurePosixPath
        self.key: ObjectKey

    def acquire(self) -> None:
        ...

    def release(self) -> None:
        ...

    def refresh(self) -> None:
        ...

    def __enter__(self) -> "Lock":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def __del__(self) -> None:
        ...
