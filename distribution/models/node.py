"""
Node model in a distributed system.
"""
from typing import List

from pydantic import Field

from datamodel.data.model import Data


class Node(Data):
    host: str
    port: int
    children: List["Node"] = Field(default_factory=list)
