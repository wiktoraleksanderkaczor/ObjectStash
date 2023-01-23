"""Group model."""
from uuid import uuid4

from pydantic import BaseModel, Field, StrictStr
from pydantic.types import UUID4


class Group(BaseModel):
    name: StrictStr = "ObjectStash"
    uuid: UUID4 = Field(default_factory=uuid4)
