"""Group model."""
from pydantic import BaseModel, Field, StrictStr

from datamodel.unique import PioneerUUID


class Group(BaseModel):
    name: StrictStr = "Pioneer"
    uuid: PioneerUUID = Field(default_factory=PioneerUUID.random)
