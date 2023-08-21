"""Models for locking."""
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from config.env import env
from datamodel.timedate import DateTime


class StorageLock(BaseModel):
    cluster: str = env.cluster.name
    timestamp: DateTime = Field(default_factory=datetime.utcnow)
    duration: timedelta = env.locking.storage.duration

    def is_expired(self) -> bool:
        return self.timestamp + self.duration < datetime.utcnow()

    def is_owned(self) -> bool:
        return self.cluster == env.cluster.name

    def valid(self) -> bool:
        if self.is_expired():
            return False
        if self.is_owned():
            return False
        return True
