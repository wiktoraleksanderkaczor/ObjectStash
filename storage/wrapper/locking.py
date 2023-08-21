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
    def __init__(
        self,
        wrapped: StorageClientInterface,
        consumers: List[SyncObjConsumer],
    ):
        super().__init__(wrapped, consumers)
        self.key = StorageKey(storage=self.__wrapped__.name, path=StoragePath(".lock"))
        self.storage_lock: StorageLock
        self.acquire()
        # Refresh the lock before it expires (90% of lock duration).
        duration_in_seconds = self.storage_lock.duration.total_seconds()
        refresh_interval = duration_in_seconds * 0.9
        scheduler.every(int(refresh_interval)).seconds.do(self.refresh)

    def acquire(self, is_refresh: bool = False) -> None:
        if self.key not in self.__wrapped__ or is_refresh:
            self.storage_lock = StorageLock()
            obj, data = Object.create_file(name=self.key, raw=self.storage_lock.json().encode())
            self.__wrapped__.put(obj, data)
        self.storage_lock: StorageLock = StorageLock.parse_raw(self.__wrapped__.get(self.key).__root__)
        if not self.storage_lock.valid():
            raise RuntimeError(f"{self.__wrapped__} already locked")

    def release(self) -> None:
        if self.storage_lock.valid() and self.key in self.__wrapped__:
            self.__wrapped__.remove(self.key)

    def refresh(self) -> None:
        if self.storage_lock.valid() and self.key in self.__wrapped__:
            return self.acquire(is_refresh=True)
        return self.acquire()

    def __enter__(self) -> StorageLock:
        self.acquire()
        return self.storage_lock

    def __exit__(self, *args, **kwargs):
        self.release()


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
