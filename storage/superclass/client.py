"""
Base class for storage clients.
"""
from abc import abstractmethod
from contextlib import contextmanager
from typing import Any, Generator, List, Union

from pysyncobj.batteries import ReplLockManager

from datamodel.data.model import Data
from distribution.superclass.distributed import Distributed
from network.superclass.scheduling import scheduler
from storage.interface.client import StorageClientInterface
from storage.models.client.info import StorageInfo
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.header.models import Header
from storage.models.object.file.data import FileData
from storage.models.object.models import Folder, Object
from storage.models.object.path import StorageKey, StoragePath
from storage.models.wrapper.locking import StorageLock


class LockConfig(Data):
    interval: int = 300
    timeout: int = 30
    grace: int = 30


class BaseStorageClient(StorageClientInterface, Distributed):
    RESERVED = [
        StoragePath(path="._mount.json"),
        StoragePath(path="._root.json"),
        StoragePath(path="._header.json"),
        StoragePath(path="._lock.json"),
    ]

    @abstractmethod
    def __init__(self, *args, interval: int = 300, grace: int = 30, timeout: int = 30, **kwargs) -> None:
        super().__init__()
        self._lock: StorageLock
        if self._lock_key in self:
            raw = self.get(self._lock_key)
            self._lock = StorageLock.from_raw(raw)
            if not self._lock.is_owned() and not self._lock.is_expired():
                raise RuntimeError(f"{self} already locked")

        self.lock()
        self.monitor = scheduler.every((interval - grace)).seconds.do(self.refresh)
        self._lock_manager = ReplLockManager(timeout)

    @property
    def _lock_key(self) -> StorageKey:
        return StorageKey(storage=self.name, path=StoragePath(path=".lock"))

    def lock(self) -> None:
        if not self.is_master():
            return
        self._lock = StorageLock()
        encoded = self._lock.to_json().encode()
        obj, data = Object.create_file(key=self._lock_key, raw=encoded)
        self.put(obj, data)

    def unlock(self) -> None:
        if self._lock.valid() and self.is_master():
            self.remove(self._lock_key)

    def refresh(self) -> None:
        if not self.is_master():
            return
        if self._lock.valid():
            return
        raise RuntimeError(f"{self} lock invalid")

    @contextmanager
    def locked(self, key: Union[StorageKey, List[StorageKey]]) -> Generator[None, Any, Any]:
        if isinstance(key, StorageKey):
            key = [key]
        try:
            for k in key:
                is_locked = self._lock_manager.tryAcquire(str(k), sync=True)
                if not is_locked:
                    raise RuntimeError(f"Could not acquire lock for {k}")
            yield
        finally:
            for k in key:
                self._lock_manager.release(str(k), sync=True)

    @contextmanager
    def transact(self, key: Union[StorageKey, List[StorageKey]]) -> Generator[None, Any, Any]:
        try:
            with self.locked(key):
                yield
        except Exception as e:
            # Rollback changes here
            raise e

    @abstractmethod
    def get(self, key: StorageKey) -> FileData:
        ...

    @abstractmethod
    def put(self, obj: Object, data: FileData) -> None:
        self.update(obj)

    @abstractmethod
    def remove(self, key: StorageKey) -> None:
        ...

    def stat(self, key: StorageKey) -> Object:
        header = self.header(key)
        return header.objects[key]

    # Might add depth limit parameter, decrease by 1 each recursive call
    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        header = self.header(prefix)
        items = list(header.objects.keys())
        if recursive:
            folders = [k for k, v in header.objects.items() if isinstance(v, Folder)]
            new = [self.list(folder, recursive) for folder in folders]
            items.extend(*new)
        return items

    def header(self, key: StorageKey) -> Header:
        """
        Headers are per directory, not including subdirectories apart from their existence.
        """
        dir_path = key.path.parent if self.stat(key).is_file() else key.path
        head_key = StorageKey(storage=key.storage, path=dir_path).join("._head.json")
        data = self.get(head_key)
        header = Header.model_validate_json(data)
        return header

    def update(self, obj: Object) -> None:
        header = self.header(obj.key)
        header.objects[obj.key] = obj
        obj, data = header.create_file()
        self.put(obj, data)

    def exists(self, key: StorageKey) -> bool:
        return key in self

    def __contains__(self, key: StorageKey) -> bool:
        try:
            self.stat(key)
        except KeyError:
            return False
        return True

    @property
    def name(self) -> StorageClientKey:
        return StorageClientKey(value=repr(self))

    @property
    def info(self) -> StorageInfo:
        key = StorageKey(storage=self.name, path=StoragePath(path="._info.json"))
        if key not in self:
            encoded = StorageInfo().to_json().encode()
            obj, data = Object.create_file(key, encoded)
            self.put(obj, data)
        raw = self.get(key)
        return StorageInfo.from_raw(raw)

    @property
    def medium(self) -> Medium:
        ...

    # Hash for Pioneer client management set replacement
    def __hash__(self):
        return hash(self.name)

    # String representation for pathing
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.info.uuid}"
