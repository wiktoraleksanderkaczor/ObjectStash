from typing import List

from cache.models.distribution import Distribution
from cache.models.objects import CacheObject


class Local(Distribution):
    def on(obj: CacheObject) -> List[str]:
        return Local.peers

    pass
