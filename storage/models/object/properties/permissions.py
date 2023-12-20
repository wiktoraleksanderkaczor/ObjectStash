"""Item permissions model."""
from typing import Dict, Optional, Union

from pydantic import Field

from auth.models.group import Group
from auth.models.user import User
from datamodel.data.model import Data


class PermissionFlags(Data):
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


class AccessControl(Data):
    default: Optional[PermissionFlags] = None
    mapping: Dict[Union[User, Group], PermissionFlags] = Field(default_factory=dict)


class PermissionInfo(Data):
    owner: Dict[Union[User, None], PermissionFlags] = Field(default_factory=lambda: (None, PermissionFlags.user()))
    group: Dict[Union[Group, None], PermissionFlags] = Field(default_factory=lambda: (None, PermissionFlags.group()))
    others: PermissionFlags = Field(default_factory=PermissionFlags.others)
    acl: Optional[AccessControl] = None
