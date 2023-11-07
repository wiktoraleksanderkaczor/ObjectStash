"""
Message model for communication between nodes.
"""
from typing import Union

from pydantic import BaseModel, Field

from datamodel.timedate import DateTime
from distribution.models.node import Node


class Message(BaseModel):
    timestamp: DateTime = Field(default_factory=DateTime.now)
    receiver: Union[Node, None] = None
    sender: Node
    content: str
