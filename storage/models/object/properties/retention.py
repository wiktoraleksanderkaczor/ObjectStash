"""Storage models."""
from enum import Enum

from pydantic import BaseModel


class RetentionClass(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    GLACIER = "GLACIER"


class RetentionInfo(BaseModel):
    storage_class: RetentionClass = RetentionClass.HOT
