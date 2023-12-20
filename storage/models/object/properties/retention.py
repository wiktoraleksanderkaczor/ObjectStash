"""Storage models."""
from enum import Enum

from datamodel.data.model import Data


class RetentionClass(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    GLACIER = "GLACIER"


class RetentionInfo(Data):
    storage_class: RetentionClass = RetentionClass.HOT
