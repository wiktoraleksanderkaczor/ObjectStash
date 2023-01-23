"""Medium model."""
from enum import Enum


class Medium(str, Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
