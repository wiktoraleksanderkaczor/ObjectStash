"""Models for locking."""
from datetime import datetime, timedelta

from pydantic import Field

from datamodel.data.model import Data
from datamodel.timedate import DateTime
from settings import config


class StorageLock(Data):
    cluster: str = config.cluster.name
    timestamp: DateTime = Field(default_factory=datetime.utcnow)
    duration: timedelta = config.storage.locking.duration

    def is_expired(self) -> bool:
        return self.timestamp + self.duration < datetime.utcnow()

    def is_owned(self) -> bool:
        return self.cluster == config.cluster.name

    def valid(self) -> bool:
        if self.is_expired():
            return False
        if self.is_owned():
            return False
        return True
