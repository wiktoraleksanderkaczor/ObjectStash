"""
Modification info model
"""
from datetime import datetime

from pydantic import BaseModel, Field

from datamodel.timedate import DateTime


class ModificationInfo(BaseModel):
    modified: DateTime = Field(default_factory=datetime.utcnow)
    created: DateTime = Field(default_factory=datetime.utcnow)
    accessed: DateTime = Field(default_factory=datetime.utcnow)
