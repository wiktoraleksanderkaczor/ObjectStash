"""Group model."""
from pydantic import Field, StrictStr

from datamodel.data.model import Data
from datamodel.unique import UniqueID


class Group(Data):
    name: StrictStr = "Users"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
