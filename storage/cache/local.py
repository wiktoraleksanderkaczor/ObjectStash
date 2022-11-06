from storage.cache.models.cache import Cache


class LocalCache(Cache):
    def __init__(self):
        super().__init__()
