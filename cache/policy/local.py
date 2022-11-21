from cache.distribution.local import Local
from cache.models.distribution import Distribution
from cache.models.policy import Policy
from cache.models.replacement import Replacement
from cache.replacement.lru import LeastRecentlyUsed
from storage.client.local import LocalClient
from storage.client.models.client import StorageClient


class Local(Policy):
    distribution: Distribution = Local
    persistence: StorageClient = LocalClient
    replacement: Replacement = LeastRecentlyUsed
