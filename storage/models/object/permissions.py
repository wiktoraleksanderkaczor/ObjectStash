"""Item permissions model."""
from typing import Dict

from pydantic import BaseModel

from auth.models.group import Group
from auth.models.user import User
from config.env import env


class PermissionFlags(BaseModel):
    read: bool = True
    write: bool = True
    execute: bool = False
    # list


class PermissionInfo(BaseModel):
    owner: User = env.cluster.user
    group: Group = env.cluster.group

    mapping: Dict[str, PermissionFlags] = {env.cluster.user.uuid.hex: PermissionFlags()}  # UUID to permissions
