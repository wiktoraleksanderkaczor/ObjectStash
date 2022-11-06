from role.distribution import Distributed
from storage.cache.models.cache import Cache


class ShardedCache(Cache, Distributed):
    def __init__(self):
        super().__init__()
