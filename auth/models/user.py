"""User model."""
from typing import List

from pydantic import BaseModel, Field
from pydantic.types import StrictStr

from auth.models.group import Group
from datamodel.unique import PioneerUUID


class User(BaseModel):
    name: StrictStr = "Pioneer"
    uuid: PioneerUUID = Field(default_factory=PioneerUUID.random)
    membership: List[Group] = [Group()]
