from datetime import datetime

from pydantic import BaseModel, Field


class ModificationInfo(BaseModel):
    modified: datetime = Field(default_factory=datetime.utcnow)
    created: datetime = Field(default_factory=datetime.utcnow)
    accessed: datetime = Field(default_factory=datetime.utcnow)
