from enum import Enum

from pydantic import BaseModel


class StorageClass(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    GLACIER = "GLACIER"


class StorageInfo(BaseModel):
    # container: StrictStr  # What is this?
    storage_class: StorageClass = StorageClass.HOT
