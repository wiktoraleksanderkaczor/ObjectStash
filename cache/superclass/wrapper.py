"""Cache wrapper superclass"""
# Need to make lower models, policy, etc. anything lower than a particular type of cache model...
# ...use generic keys (dunno even) and values (bytes)
# Classes that act as a sort of middle layer, handling conversions to the caching function inputs, like Object or bytes?
from typing import Dict, Type

from cache.interface.replacement import ReplacementInterface
from cache.interface.wrapper import CacheWrapperInterface
from storage.interface.client import StorageClientInterface
from storage.interface.path import ObjectKey
from storage.models.item.content import ObjectData
from storage.models.item.models import Object


class BaseCacheWrapper(CacheWrapperInterface):
    subclasses: Dict[str, Type["BaseCacheWrapper"]] = {}

    def __init__(self, wrapped: object, storage: StorageClientInterface, replacement: ReplacementInterface):
        self.hits = 0
        self.misses = 0
        self.wrapped = wrapped
        self.storage = storage
        self.replacement = replacement

    def __init_subclass__(cls: Type["BaseCacheWrapper"], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__name__] = cls

    def _get(self, item: ObjectKey) -> ObjectData:
        return self.storage.get(item)

    def _put(self, item: Object, data: ObjectData):
        return self.storage.put(item, data)

    # Only called when not in current object, error when no such attr
    def __getattribute__(self, attr: str) -> object:
        return getattr(self.wrapped, attr)

    # One can attach new things to cache via:
    # Cache.func_to_cache = func
    # No idea how to have things cached by default tho.
    # Additional subclasses with things like TableCache could do good defaults?
    # Especially since user can delete functions from instances hehe


# Maybe define some __getattr__ to use policy and such automatically?
# Need some scheduling for cache rebalancing too.
