from pydantic import BaseModel

from cache.models.distribution import Distribution
from cache.models.persistance import Persistence
from cache.models.replacement import Replacement
from cache.persistence.memory import Memory
from cache.replacement.lru import LeastRecentlyUsed


# Globally can be sharded, replicated etc. and local can be memory, disk etc. finally, replacement can be LRU etc.
class Policy(BaseModel):
    distribution: Distribution
    persistence: Persistence = Memory
    replacement: Replacement = LeastRecentlyUsed
