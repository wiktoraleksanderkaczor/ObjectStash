from typing import List

from cache.models.cache import Cache
from cache.models.policy import Policy
from storage.client.models.objects import Object, ObjectID


class Storage(Cache):
    def __init__(self, wrapped: object, policy: Policy):
        super().__init__(wrapped, policy)

    def get(self, key: ObjectID) -> Object:
        ...

    def exists(self, key: ObjectID) -> bool:
        ...

    def items(self) -> List[ObjectID]:
        ...
