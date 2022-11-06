from pydantic import Protocol

from storage.client.models.objects import Key, Object


class Cache(Protocol):
    def __init__(self):
        self.hits = 0
        self.misses = 0

    def get(self, key: Key) -> Object:
        ...
