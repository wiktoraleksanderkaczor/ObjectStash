"""Item permissions model."""
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field

from auth.models.group import Group
from auth.models.user import User


class PermissionFlags(BaseModel):
    read: bool = True
    write: bool = True
    execute: bool = False

    @classmethod
    def user(cls) -> "PermissionFlags":
        return PermissionFlags(read=True, write=True, execute=False)

    @classmethod
    def group(cls) -> "PermissionFlags":
        return PermissionFlags(read=True, write=True, execute=False)

    @classmethod
    def others(cls) -> "PermissionFlags":
        return PermissionFlags(read=True, write=False, execute=False)


class AccessControl(BaseModel):
    default: Optional[PermissionFlags] = None
    mapping: Dict[Union[User, Group], PermissionFlags] = Field(default_factory=dict)


class PermissionInfo(BaseModel):
    owner: Dict[Union[User, None], PermissionFlags] = Field(default_factory=lambda: (None, PermissionFlags.user()))
    group: Dict[Union[Group, None], PermissionFlags] = Field(default_factory=lambda: (None, PermissionFlags.group()))
    others: PermissionFlags = Field(default_factory=PermissionFlags.others)
    acl: Optional[AccessControl] = None
