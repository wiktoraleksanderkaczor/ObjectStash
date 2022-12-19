from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.types import UUID4, StrictStr

from .group import Group


class User(BaseModel):
    name: StrictStr = "ObjectStash"
    uuid: UUID4 = Field(default_factory=uuid4)
    membership: List[Group] = [Group()]
