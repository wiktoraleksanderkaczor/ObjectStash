# Need to make lower models, policy, etc. anything lower than a particular type of cache model...
# ...use generic keys (dunno even) and values (bytes)

from typing import List, Union

from pydantic import Protocol

from cache.models.policy import Policy
from database.models.databases import JSONish
from storage.client.models.objects import ObjectID, ObjectInfo


class Cache(Protocol):
    def __init__(self, wrapped: object):
        self.hits = 0
        self.misses = 0
        self.wrapped = wrapped

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
class PartitionCache(Cache):
    def __init__(self, wrapped: object, policy: Policy):
        super().__init__(wrapped)
        self.policy = policy

    def get(self, keys: Union[ObjectInfo, List[ObjectID]]) -> JSONish:
        ...

    def exists(self, keys: Union[ObjectID, List[ObjectID]]) -> List[ObjectID]:
        ...

    def items(self) -> List[ObjectID]:
        ...
