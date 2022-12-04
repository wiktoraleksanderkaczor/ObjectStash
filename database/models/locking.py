from datetime import datetime, timedelta

from pydantic import BaseModel, Protocol

from config.env import env
from storage.models.client import StorageClient


class LockData(BaseModel):
    cluster: str
    timestamp: datetime
    duration: timedelta


class Lock(Protocol):
    def lock():
        ...

    def unlock():
        ...

    def check(self):
        self.storage.get_object(self.fname) if self.storage.object_exists(self.fname) else None
        ...

    def new(self):
        return LockData(
            cluster=env.cluster.name,
            timestamp=datetime.utcnow(),
            duration=env.storage[self.storage.name].locking.duration,
        )

    def __init__(self, storage: StorageClient, prefix):
        self.storage = storage
        self.prefix = prefix
        self.fname = self.prefix + env.storage[storage.name].filename.lock
        self.state: LockData = self.check()
        if self.state.cluster == env.cluster.name:
            self.lock()
