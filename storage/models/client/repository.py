"""Repository model."""
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field


class Repository(BaseModel):
    name: str = "ObjectStash"
    uuid: UUID4 = Field(default_factory=uuid4)
