"""Repository model."""
from pydantic import Field

from datamodel.data.model import Data
from datamodel.unique import UniqueID


class StorageInfo(Data):
    uuid: UniqueID = Field(default_factory=UniqueID.random)
