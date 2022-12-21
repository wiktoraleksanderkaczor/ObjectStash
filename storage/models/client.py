from typing import List

from storage.models.capabilities import Capability
from storage.models.medium import Medium
from storage.models.objects import Object, ObjectID, ObjectInfo

# Handling singular and multiple object operations is done by calling the singular function multiple times by default
# If client has appropriate efficient functions, that can be called instead
# At a minimum, to implement the class, one requires;
# - all singular operations
# - all multiple operations without a singular alternative


class StorageClient:
    CLIENT_NAME: str
    CAPABILITIES: List[Capability]
    MEDIUM: Medium

    def __init__(
        self,
        container: str,
        *args,
        **kwargs,
    ):
        self.client = None
        self.container = container

    # REQUIRED:

    def container_exists(self) -> bool:
        ...

    def create_container(self) -> bool:
        ...

    def list_objects(self, prefix: ObjectID, recursive: bool = False) -> List[ObjectID]:
        ...

    def get_object(self, key: ObjectID) -> Object:
        ...

    def put_object(self, obj: Object) -> bool:
        ...

    def stat_object(self, key: ObjectID) -> ObjectInfo:
        ...

    def remove_object(self, key: ObjectID) -> bool:
        ...

    # OPTIONAL:

    def get_objects(self, keys: List[ObjectID]) -> List[Object]:
        return [self.get_object(key) for key in keys]

    def put_objects(self, data: List[Object]) -> List[bool]:
        return [self.put_object(item) for item in data]

    def stat_objects(self, keys: List[ObjectID]) -> List[ObjectInfo]:
        return [self.stat_object(key) for key in keys]

    def remove_objects(self, keys: List[ObjectID]) -> List[bool]:
        return [self.remove_object(key) for key in keys]

    def object_exists(self, key: ObjectID) -> bool:
        return key in self.list_objects(key.parent)
