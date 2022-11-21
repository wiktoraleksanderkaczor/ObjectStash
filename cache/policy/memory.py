from cache.distribution.local import Local
from cache.models.distribution import Distribution
from cache.models.policy import Policy
from cache.models.replacement import Replacement
from cache.replacement.lru import LeastRecentlyUsed
from storage.client.memory import MemoryClient
from storage.client.models.client import StorageClient


class Memory(Policy):
    distribution: Distribution = Local
    persistence: StorageClient = MemoryClient
    replacement: Replacement = LeastRecentlyUsed
