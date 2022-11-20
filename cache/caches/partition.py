from typing import List

from cache.models.cache import Cache
from cache.models.policy import Policy
from database.models.databases import JSONish
from storage.client.models.objects import ObjectID


class Partition(Cache):
    def __init__(self, wrapped: object, policy: Policy):
        super().__init__(wrapped, policy)

    def get(self, key: ObjectID) -> JSONish:
        ...

    def exists(self, key: ObjectID) -> bool:
        ...

    def items(self) -> List[ObjectID]:
        ...
