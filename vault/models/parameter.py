"""Parameter model."""
from typing import Dict

from datamodel.data import JSON


class Parameter(JSON):
    name: str
    value: str
    tags: Dict[str, str]
