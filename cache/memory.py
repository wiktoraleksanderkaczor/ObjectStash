from cache.models.cache import Cache


class MemoryCache(Cache):
    def __init__(self):
        super().__init__()
