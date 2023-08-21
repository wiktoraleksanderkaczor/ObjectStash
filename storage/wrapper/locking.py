"""
This module contains the implementation of a storage locking wrapper for the storage client.
"""
from typing import List

from pysyncobj import SyncObjConsumer
from pysyncobj.batteries import ReplLockManager

from network.superclass.scheduling import scheduler
from storage.interface.client import StorageClientInterface
from storage.models.object.file.info import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath
from storage.models.wrapper.locking import StorageLock
from storage.wrapper.interface import StorageWrapper


# Add acquiry timeouts
class StorageLockingWrapper(StorageWrapper):
    RESERVED: List[StoragePath] = [StoragePath(".lock")]

    def __init__(
        self,
        wrapped: StorageClientInterface,
        consumers: List[SyncObjConsumer],
        interval: int = 300,
        grace: int = 30,
    ):
        super().__init__(wrapped, consumers)
        self._lock: StorageLock
        if self._lock_key in self.__wrapped__:
            decoded = self.__wrapped__.get(self._lock_key).to_text()
            self._lock = StorageLock.parse_raw(decoded)
            if not self._lock.is_owned() and not self._lock.is_expired():
                raise RuntimeError(f"{self.__wrapped__} already locked")

        self.lock()
        self.monitor = scheduler.every((interval - grace)).seconds.do(self.refresh)

    def lock(self) -> None:
        if not self.is_master():
            return
        self._lock = StorageLock()
        encoded = self._lock.json().encode()
        obj, data = Object.create_file(name=self._lock_key, raw=encoded)
        self.__wrapped__.put(obj, data)

    def unlock(self) -> None:
        if self._lock.valid() and self.is_master():
            self.__wrapped__.remove(self._lock_key)

    def refresh(self) -> None:
        if not self.is_master():
            return
        if self._lock.valid():
            return
        raise RuntimeError(f"{self.__wrapped__} lock invalid")

    @property
    def _lock_key(self) -> StorageKey:
        return StorageKey(storage=self.__wrapped__.name, path=StoragePath(".lock"))


class ObjectLockingWrapper(StorageLockingWrapper):
    def __init__(self, wrapped: StorageClientInterface, consumers: List[SyncObjConsumer], timeout: int = 30):
        super().__init__(wrapped, consumers)
        self._lock_manager = ReplLockManager(timeout)  # , self.__wrapped__.name)

    def get(self, key: StorageKey) -> FileData:
        lock_id = str(key.path)
        is_locked = self._lock_manager.tryAcquire(str(key.path), sync=True)
        if not is_locked:
            raise RuntimeError(f"Could not acquire lock for {key}")
        resp = super().get(key)
        self._lock_manager.release(lock_id, sync=True)
        return resp

    def put(self, obj: Object, data: FileData) -> None:
        lock_id = str(obj.name.path)
        is_locked = self._lock_manager.tryAcquire(lock_id, sync=True)
        if not is_locked:
            raise RuntimeError(f"Could not acquire lock for {lock_id}")
        super().put(obj, data)
        self._lock_manager.release(lock_id, sync=True)

    def remove(self, key: StorageKey) -> None:
        lock_id = str(key.path)
        is_locked = self._lock_manager.tryAcquire(lock_id, sync=True)
        if not is_locked:
            raise RuntimeError(f"Could not acquire lock for {lock_id}")
        super().remove(key)
        self._lock_manager.release(lock_id, sync=True)
