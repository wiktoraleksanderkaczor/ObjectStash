"""Repository model."""
from pydantic import BaseModel, Field

from datamodel.unique import PioneerUUID


class Repository(BaseModel):
    name: str = "Pioneer"
    uuid: PioneerUUID = Field(default_factory=PioneerUUID.random)
