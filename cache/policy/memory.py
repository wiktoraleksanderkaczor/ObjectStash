from cache.distribution.local import Local
from cache.models.distribution import Distribution
from cache.models.persistance import Persistence
from cache.models.policy import Policy
from cache.models.replacement import Replacement
from cache.persistence.memory import Memory
from cache.replacement.lru import LeastRecentlyUsed


class Memory(Policy):
    distribution: Distribution = Local
    persistence: Persistence = Memory
    replacement: Replacement = LeastRecentlyUsed
