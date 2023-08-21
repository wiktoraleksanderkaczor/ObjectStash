"""Repository model."""
from pydantic import BaseModel, Field

from datamodel.unique import UniqueID


class StorageInfo(BaseModel):
    # name: str = "Pioneer"
    uuid: UniqueID = Field(default_factory=UniqueID.random)
