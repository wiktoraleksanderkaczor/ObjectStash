from datetime import datetime, timedelta

from pydantic import BaseModel, Protocol

from config.env import env
from role.distribution import Distributed
from storage.models.client import StorageClient


class LockData(BaseModel):
    cluster: str
    timestamp: datetime
    duration: timedelta


class Lock(Protocol):
    def lock(self):
        ...

    def unlock(self):
        if self.storage.object_exists(self.fname):
            return self.storage.remove_object(self.fname)
        return True

    def check(self) -> LockData:
        self.storage.get_object(self.fname) if self.storage.object_exists(self.fname) else self.new()

    def new(self):
        return LockData(
            cluster=env.cluster.name,
            timestamp=datetime.utcnow(),
            duration=env.storage[self.storage.name].locking.duration,
        )

    def is_valid(self) -> bool:
        # Check if lock if valid and locked
        pass

    def __init__(self, storage: StorageClient, prefix):
        self.storage = storage
        self.prefix = prefix
        self.fname = self.prefix + env.storage[storage.name].filename.lock
        self.state: LockData = self.check()
        if self.state.cluster != env.cluster.name:
            self.lock()


class DistributedLock(Lock):
    def __init__(self, storage: StorageClient, prefix):
        super().__init__(storage, prefix)
        Distributed.__init__(self, ":".join(storage.name, prefix), consumers=[self.state])

    def __del__(self):
        is_last_node = len(self.otherNodes) == 0 and self.isReady()
        if self.state and is_last_node:  # and is last node
            self.unlock()
        return super().__del__()
