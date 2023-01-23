# Need to make lower models, policy, etc. anything lower than a particular type of cache model...
# ...use generic keys (dunno even) and values (bytes)
# Classes that act as a sort of middle layer, handling conversions to the caching function inputs, like Object or bytes?
from abc import ABC, abstractmethod
from typing import Dict, Type

from cache.interface.replacement import ReplacementInterface
from storage.interface.client import StorageClient
from storage.interface.path import ObjectKey
from storage.models.item.content import ObjectData
from storage.models.item.models import Object


class CacheWrapperInterface(ABC):
    subclasses: Dict[str, Type["CacheWrapperInterface"]]

    @abstractmethod
    def __init__(self, wrapped: object, storage: StorageClient, replacement: ReplacementInterface):
        self.hits: int
        self.misses: int
        self.wrapped: object
        self.storage: StorageClient
        self.replacement: ReplacementInterface

    @abstractmethod
    def __init_subclass__(cls: Type["CacheWrapperInterface"], **kwargs):
        ...

    @abstractmethod
    def _get(self, item: ObjectKey) -> ObjectData:
        ...

    @abstractmethod
    def _put(self, item: Object, data: ObjectData):
        ...

    # Only called when not in current object, error when no such attr
    @abstractmethod
    def __getattribute__(self, attr: str) -> object:
        ...

    # One can attach new things to cache via:
    # Cache.func_to_cache = func
    # No idea how to have things cached by default tho.
    # Additional subclasses with things like TableCache could do good defaults?
    # Especially since user can delete functions from instances hehe


# Maybe define some __getattr__ to use policy and such automatically?
# Need some scheduling for cache rebalancing too.
