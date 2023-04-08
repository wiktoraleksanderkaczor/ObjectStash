"""Models for locking."""
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from config.env import env
from datamodel.timedate import DateTime


class StorageLock(BaseModel):
    cluster: str = env.cluster.name
    timestamp: DateTime = Field(default_factory=datetime.utcnow)
    duration: timedelta = env.locking.storage.duration

    def valid(self) -> bool:
        if self.timestamp + self.duration < datetime.utcnow():
            return False
        if self.cluster != env.cluster.name:
            return False
        return True
