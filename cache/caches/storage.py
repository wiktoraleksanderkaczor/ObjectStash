from typing import List

from cache.models.cache import Cache
from cache.models.policy import Policy
from storage.client.models.objects import Object, ObjectID, ObjectInfo


class Storage(Cache):
    def __init__(self, wrapped: object, policy: Policy):
        super().__init__(wrapped, policy)

    def container_exists(self) -> bool:
        ...

    def get_object(self, key: ObjectID) -> Object:
        ...

    def stat_object(self, key: ObjectID) -> ObjectInfo:
        ...

    def list_objects(self, prefix: ObjectID, recursive: bool = False) -> List[ObjectID]:
        ...
