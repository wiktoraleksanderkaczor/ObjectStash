from datetime import datetime, timedelta

from pydantic import BaseModel, Protocol

from config.env import env
from storage.client.models.client import StorageClient


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
            cluster=env["CLUSTER"]["NAME"],
            timestamp=datetime.utcnow(),
            duration=timedelta(**env["STORAGE"][self.storage.name]["LOCK"]["DURATION"]),
        )

    def __init__(self, storage: StorageClient, prefix, fname=".lock"):
        self.storage = storage
        self.prefix = prefix
        self.fname = self.prefix + fname
        self.state: LockData = self.check()
        if self.state.cluster == env["CLUSTER"]["NAME"]:
            self.lock()
