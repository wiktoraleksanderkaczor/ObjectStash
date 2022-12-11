from datetime import datetime, timedelta

from pydantic import BaseModel

from config.env import env


class State(BaseModel):
    cluster: str = env.cluster.name
    timestamp: datetime = datetime.utcnow()
    duration: timedelta
