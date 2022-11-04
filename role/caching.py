from ..models.caching import Cache
from .distribution import Distributed


class MemoryCache(Cache):
    def __init__(self):
        super().__init__()
        self.data = {}


class LocalCache(Cache):
    def __init__(self):
        super().__init__()


class ShardedCache(Cache, Distributed):
    def __init__(self):
        super().__init__()


class ReplicatedCache(Cache, Distributed):
    pass


class IntelligentCache(Cache):
    pass
