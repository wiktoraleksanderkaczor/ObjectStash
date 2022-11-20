# Defines a model for persistency, operations like cache.get and cache.set for raw data, bytes essentially, compatible

from pydantic import Protocol

from cache.models.objects import CacheKey, CacheObject


class Persistence(Protocol):
    def get(key: CacheKey) -> object:
        ...

    def set(key: CacheKey, obj: CacheObject) -> bool:
        ...

    def remove(key: CacheKey) -> bool:
        ...
