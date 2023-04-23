"""
Object metadata model
"""
from typing import Set

from pydantic import BaseModel, Field

from storage.models.object.modification import ModificationInfo
from storage.models.object.permissions import PermissionInfo
from storage.models.object.storage import StorageInfo


class ObjectMetadata(BaseModel):
    storage: StorageInfo = StorageInfo()
    permissions: PermissionInfo = PermissionInfo()
    when: ModificationInfo = ModificationInfo()
    tags: Set[str] = Field(default_factory=set)
