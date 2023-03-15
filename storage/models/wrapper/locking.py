"""Models for locking."""
import pickle
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from config.env import env


class Lock(BaseModel):
    cluster: str = env.cluster.name
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration: timedelta = env.locking.duration

    def to_bytes(self) -> bytes:
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def from_bytes(data: bytes) -> "Lock":
        return pickle.loads(data)
