from role.distribution import Distributed
from storage.cache.models.cache import Cache


class ReplicatedCache(Cache, Distributed):
    pass
