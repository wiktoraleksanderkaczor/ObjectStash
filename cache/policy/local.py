from cache.distribution.local import Local
from cache.models.distribution import Distribution
from cache.models.persistance import Persistence
from cache.models.policy import Policy
from cache.models.replacement import Replacement
from cache.persistence.filesystem import Filesystem
from cache.replacement.lru import LeastRecentlyUsed


class Local(Policy):
    distribution: Distribution = Local
    persistence: Persistence = Filesystem
    replacement: Replacement = LeastRecentlyUsed
