"""
Modification info model
"""
from pydantic import BaseModel, Field

from datamodel.timedate import DateTime


class AccessTimeInfo(BaseModel):
    modified: DateTime = Field(default_factory=DateTime.utcnow)
    created: DateTime = Field(default_factory=DateTime.utcnow)
    accessed: DateTime = Field(default_factory=DateTime.utcnow)
