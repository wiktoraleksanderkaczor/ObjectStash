from typing import Optional

from pydantic import BaseModel

from cache.models.persistance import Persistence
from cache.models.replacement import Replacement
from cache.policy.memory import MemoryCache
from cache.replacement.lru import LeastRecentlyUsed


# Globally can be sharded, replicated etc. and local can be memory, disk etc. finally, replacement can be LRU etc.
class Policy(BaseModel):
    globally: Persistence
    locally: Optional[Persistence] = MemoryCache
    replacement: Replacement = LeastRecentlyUsed
