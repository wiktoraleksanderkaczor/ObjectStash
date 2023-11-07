"""
Node model in a distributed system.
"""
from typing import List

from pydantic import BaseModel, Field


class Node(BaseModel):
    host: str
    port: int
    children: List["Node"] = Field(default_factory=list)
