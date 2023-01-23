"""Version info model."""
from pydantic import BaseModel

from storage.models.item.modification import ModificationInfo


class VersionInfo(BaseModel):
    is_deleted: bool = False
    is_latest: bool = True
    when: ModificationInfo = ModificationInfo()
