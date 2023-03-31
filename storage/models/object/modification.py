"""
Modification info model
"""
from datetime import datetime

from pydantic import BaseModel, Field

from datamodel.timedate import PioneerDateTime


class ModificationInfo(BaseModel):
    modified: PioneerDateTime = Field(default_factory=datetime.utcnow)
    created: PioneerDateTime = Field(default_factory=datetime.utcnow)
    accessed: PioneerDateTime = Field(default_factory=datetime.utcnow)
