from pydantic import Protocol

from models.objects import Object

from .objects import Key


class Cache(Protocol):
    def __init__(self):
        self.hits = 0
        self.misses = 0

    def get(self, key: Key) -> Object:
        ...
