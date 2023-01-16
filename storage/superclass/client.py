from typing import Dict, List, Tuple, Union

from config.models.env import StorageConfig
from storage.interface.client import StorageClient as StorageClientInterface
from storage.interface.path import DirectoryKey, ObjectKey, StorageKey
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.item import Directory, Object, ObjectData


class BaseStorageClient(StorageClientInterface):
    initialized: Dict[StorageClientKey, StorageClientInterface] = {}

    def __init__(self, config: StorageConfig):
        self.client = None
        self.config = config
        self.initialized[self.name] = self

    # REQUIRED:

    def get(self, key: ObjectKey) -> ObjectData:
        ...

    def stat(self, key: StorageKey) -> Union[Object, Directory]:
        ...

    def put(self, obj: Object, data: ObjectData) -> None:
        ...

    def remove(self, key: StorageKey) -> None:
        ...

    def list(self, prefix: DirectoryKey, recursive: bool = False) -> List[ObjectKey]:
        ...

    @property
    def name(self) -> StorageClientKey:
        return StorageClientKey(repr(self))

    @property
    def medium(self) -> Medium:
        ...

    # OPTIONAL:
    def exists(self, key: StorageKey) -> bool:
        try:
            self.stat(key)
            return True
        except Exception:
            return False

    def get_multiple(self, *keys: ObjectKey) -> List[ObjectData]:
        return [self.get(key) for key in keys]

    def stat_multiple(self, *keys: StorageKey) -> List[Union[Object, Directory]]:
        return [self.stat(key) for key in keys]

    def put_multiple(self, *objects: Tuple[Object, ObjectData]) -> List[None]:
        return [self.put(obj, data) for obj, data in objects]

    def remove_multiple(self, *keys: ObjectKey) -> List[None]:
        return [self.remove(key) for key in keys]

    def exists_multiple(self, *keys: ObjectKey) -> List[bool]:
        return [self.exists(key) for key in keys]

    # MISCELLANEOUS:

    # Hash for ObjectStash client management set replacement
    def __hash__(self):
        return hash(self.name)

    # String representation for pathing
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.config.repository.name}({self.config.repository.uuid})"
