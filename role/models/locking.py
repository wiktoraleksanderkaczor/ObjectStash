# from datetime import datetime, timedelta

# from pydantic import BaseModel, Field

# from config.env import env


# class State(BaseModel):
#     cluster: str = env.cluster.name
#     timestamp: datetime = Field(default_factory=datetime.utcnow)
#     duration: timedelta
