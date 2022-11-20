from cache.models.distribution import Distribution
from role.distribution import Distributed


class Replicated(Distribution, Distributed):
    def __init__(self):
        super().__init__()
        Distributed.__init__(self, "ReplicatedCache")
