"""Group model."""
from pydantic import Field, StrictStr

from datamodel.data import JSON
from datamodel.unique import UniqueID


class Group(JSON):
    name: StrictStr = "Pioneer"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
