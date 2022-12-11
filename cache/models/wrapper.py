# Need to make lower models, policy, etc. anything lower than a particular type of cache model...
# ...use generic keys (dunno even) and values (bytes)
# Classes that act as a sort of middle layer, handling conversions to the caching function inputs, like Object or bytes?

from pydantic import Protocol

from cache.models.replacement import Replacement
from storage.models.client import StorageClient
from storage.models.objects import Object, ObjectID


class CacheWrapper(Protocol):
    def __init__(self, wrapped: object, storage: StorageClient, replacement: Replacement):
        self.hits = 0
        self.misses = 0
        self.wrapped = wrapped
        self.replacement = replacement
        self.storage = storage

    def _get(self, item: ObjectID):
        return self.storage.get_object(item)

    def _put(self, item: Object):
        return self.storage.put_object(item)

    # Only called when not in current object, error when no such attr
    def __getattribute__(self, attr):
        return getattr(self.wrapped, attr)

    # One can attach new things to cache via:
    # Cache.func_to_cache = func
    # No idea how to have things cached by default tho.
    # Additional subclasses with things like TableCache could do good defaults?
    # Especially since user can delete functions from instances hehe


# Maybe define some __getattr__ to use policy and such automatically?
# Need some scheduling for cache rebalancing too.
