"""
This module contains the implementation of a storage locking wrapper for the storage client.
"""
from datetime import datetime
from typing import List

from pysyncobj import SyncObjConsumer

from config.env import env
from role.superclass.scheduling import scheduler
from storage.interface.client import StorageClientInterface
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath
from storage.models.wrapper.locking import Lock
from storage.wrapper.interface import StorageWrapper


class LockingWrapper(StorageWrapper):
    def __init__(
        self,
        wrapped: StorageClientInterface,
        path: StoragePath,
        consumers: List[SyncObjConsumer],
    ):
        super().__init__(wrapped, consumers)
        self.key = StorageKey(storage=self.__wrapped__.name, path=path)
        self.data: Lock
        if not self.valid():
            self.acquire()
        else:
            raise RuntimeError(f"{self.__wrapped__} already locked")
        # Refresh the lock before it expires (90% of lock duration).
        duration_in_seconds = self.data.duration.total_seconds()
        refresh_interval = duration_in_seconds * 0.9
        scheduler.every(int(refresh_interval)).seconds.do(self.refresh)

    def valid(self) -> bool:
        if self.key in self.__wrapped__:
            obj = self.__wrapped__.get(self.key)
            self.data = Lock.from_bytes(obj.__root__)
            if self.data.timestamp + self.data.duration < datetime.utcnow():
                return False
            if self.data.cluster != env.cluster.name:
                return False
            return True
        return False

    def acquire(self) -> None:
        self.data = Lock()
        obj, data = Object.create(storage=self.key.storage, path=self.key.path, raw=self.data.to_bytes())
        self.__wrapped__.put(obj, data)

    def release(self) -> None:
        if self.key in self.__wrapped__:
            self.__wrapped__.remove(self.key)

    def refresh(self) -> None:
        if self.valid():
            self.acquire()
