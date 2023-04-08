"""Group model."""
from pydantic import BaseModel, Field, StrictStr

from datamodel.unique import UniqueID


class Group(BaseModel):
    name: StrictStr = "Pioneer"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
