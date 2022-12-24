from enum import Enum


class ItemType(str, Enum):
    CONTAINER = "CONTAINER"
    DIRECTORY = "DIRECTORY"
    FILE = "FILE"
