from cache.models.cache import Cache
from role.distribution import Distributed


class ReplicatedCache(Cache, Distributed):
    def __init__(self):
        super().__init__()
        Distributed.__init__(self, "ReplicatedCache")
