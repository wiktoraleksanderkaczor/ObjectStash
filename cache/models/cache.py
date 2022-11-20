# Need to make lower models, policy, etc. anything lower than a particular type of cache model...
# ...use generic keys (dunno even) and values (bytes)
# Classes that act as a sort of middle layer, handling conversions to the caching function inputs, like Object or bytes?

from pydantic import Protocol

from cache.models.policy import Policy


class Cache(Protocol):
    def __init__(self, wrapped: object, policy: Policy):
        self.hits = 0
        self.misses = 0
        self.wrapped = wrapped
        self.policy = policy

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
