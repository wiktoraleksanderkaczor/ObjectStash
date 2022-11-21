from datetime import timedelta
from typing import List

from pydantic import BaseModel


class Cluster(BaseModel):
    name: str
    port: int


class Lock(BaseModel):
    duration: timedelta


class Storage(BaseModel):
    container: str
    lock: Lock
    access_key: str
    secret_key: str


class Config(BaseModel):
    cluster: Cluster
    storage: List[Storage]
