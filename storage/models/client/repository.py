"""Repository model."""
from pydantic import BaseModel, Field

from datamodel.unique import UniqueID


class Repository(BaseModel):
    name: str = "Pioneer"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
