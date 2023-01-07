from enum import Enum


class ItemType(str, Enum):
    DIRECTORY = "DIRECTORY"
    FILE = "FILE"
