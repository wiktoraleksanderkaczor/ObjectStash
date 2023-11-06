"""User model."""
from typing import List

from pydantic import Field
from pydantic.types import StrictStr

from auth.models.group import Group
from datamodel.data import JSON
from datamodel.unique import UniqueID


class User(JSON):
    name: StrictStr = "Pioneer"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
    membership: List[Group] = [Group()]
