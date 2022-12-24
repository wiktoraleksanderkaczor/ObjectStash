from pydantic import BaseModel

from auth.models.group import Group
from auth.models.user import User
from config.env import env


class OwnershipInfo(BaseModel):
    owner: User = env.cluster.user
    group: Group = env.cluster.group
