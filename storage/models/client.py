"""
StorageClient is the base class for all storage clients. It consists of a set of required and optional functions.
Available operations are get, put, head and list in the {operation}_{item} format and exists in the {item}_exists format.
Multiple-based variants of those operations are also available. Those can act on the following base types:
- Object
- Directory
- Container
- Item (superset of Object and Directory)

"""
from typing import List, Tuple, Union

from storage.models.capabilities import Capability
from storage.models.item.content import ObjectContentInfo
from storage.models.item.data import ObjectData
from storage.models.item.models import Container, Directory, Object
from storage.models.item.paths import ContainerPath, DirectoryPath, ObjectPath, StoragePath
from storage.models.medium import Medium

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

    def head_container(self) -> Container:
        ...

    def put_container(self, container: ContainerPath) -> bool:
        ...

    def head_object(self, key: ObjectPath) -> Object:
        ...

    def get_object(self, key: ObjectPath) -> Tuple[Object, ObjectData]:
        ...

    def put_object(self, obj: Object) -> bool:
        ...

    def remove_object(self, key: ObjectPath) -> bool:
        ...

    def list_objects(self, prefix: DirectoryPath, recursive: bool = False) -> List[ObjectPath]:
        ...

    def head_item(self, key: StoragePath) -> Union[Object, Directory]:
        ...

    # OPTIONAL:

    def get_objects(self, keys: List[ObjectPath]) -> List[Tuple[Object, ObjectData]]:
        return [self.get_object(key) for key in keys]

    def put_objects(self, data: List[Object]) -> List[bool]:
        return [self.put_object(item) for item in data]

    def head_items(self, keys: List[StoragePath]) -> List[Union[Object, Directory]]:
        return [self.head_item(key) for key in keys]

    def remove_objects(self, keys: List[ObjectPath]) -> List[bool]:
        return [self.remove_object(key) for key in keys]

    def object_exists(self, key: ObjectPath) -> bool:
        return key in self.list_objects(DirectoryPath(self, str(key.parent)))

    def to_object(self, key: str, raw: bytes) -> Object:
        name = ObjectPath(self, key)
        data = ObjectData(__root__=raw)
        content = ObjectContentInfo.from_object(name, data)
        return Object(name=name, content=content)
