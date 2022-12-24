from typing import Dict

from pydantic import BaseModel

from config.env import env


class PermissionFlags(BaseModel):
    read: bool = True
    write: bool = True
    execute: bool = False
    # list


class PermissionInfo(BaseModel):
    mapping: Dict[str, PermissionFlags] = {env.cluster.user.uuid.hex: PermissionFlags()}  # UUID to permissions
