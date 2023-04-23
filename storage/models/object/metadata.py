"""
Object metadata model
"""
from typing import Set

from pydantic import BaseModel, Field

from storage.models.object.properties.access import AccessTimeInfo
from storage.models.object.properties.permissions import PermissionInfo
from storage.models.object.properties.retention import RetentionInfo


class Metadata(BaseModel):
    storage: RetentionInfo = RetentionInfo()
    permissions: PermissionInfo = PermissionInfo()
    access: AccessTimeInfo = AccessTimeInfo()
    tags: Set[str] = Field(default_factory=set)
