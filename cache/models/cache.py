from pydantic import Protocol


class Cache(Protocol):
    def __init__(
        self,
    ):
        self.hits = 0
        self.misses = 0
