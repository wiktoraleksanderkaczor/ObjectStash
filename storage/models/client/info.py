"""Repository model."""
from pydantic import BaseModel, Field

from datamodel.unique import UniqueID


class StorageInfo(BaseModel):
    uuid: UniqueID = Field(default_factory=UniqueID.random)
