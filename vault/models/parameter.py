"""Parameter model."""
from typing import Dict

from datamodel.data import PioneerBaseModel


class Parameter(PioneerBaseModel):
    name: str
    value: str
    tags: Dict[str, str]
