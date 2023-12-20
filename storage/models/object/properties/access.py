"""
Modification info model
"""
from pydantic import Field

from datamodel.data.model import Data
from datamodel.timedate import DateTime


class AccessTimeInfo(Data):
    modified: DateTime = Field(default_factory=DateTime.utcnow)
    created: DateTime = Field(default_factory=DateTime.utcnow)
    accessed: DateTime = Field(default_factory=DateTime.utcnow)
