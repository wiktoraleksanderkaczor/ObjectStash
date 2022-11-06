from enum import Enum


class Capability(str, Enum):
    BASIC = "BASIC"
    STREAMS = "STREAMS"
    INSERT = "INSERT"
