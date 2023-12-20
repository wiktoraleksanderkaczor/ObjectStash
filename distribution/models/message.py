"""
Message model for communication between nodes.
"""
from typing import Optional

from pydantic import Field

from datamodel.data.model import Data
from datamodel.timedate import DateTime
from distribution.models.node import Node


class Message(Data):
    timestamp: DateTime = Field(default_factory=DateTime.now)
    receiver: Optional[Node] = None
    sender: Node
    content: str
