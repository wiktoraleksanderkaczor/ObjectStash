"""
Object metadata model
"""
from typing import Set

from pydantic import BaseModel, Field

from storage.models.object.permissions import PermissionInfo
from storage.models.object.storage import StorageInfo
from storage.models.object.version import VersionInfo


class ObjectMetadata(BaseModel):
    storage: StorageInfo = StorageInfo()
    permissions: PermissionInfo = PermissionInfo()
    version: VersionInfo = VersionInfo()
    tags: Set[str] = Field(default_factory=set)
