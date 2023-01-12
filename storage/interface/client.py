from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union

from config.models.env import StorageConfig
from storage.interface.path import DirectoryKey, ObjectKey, StorageKey
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.item import Directory, Object, ObjectData


class StorageClient(ABC):
    initialized: Dict[StorageClientKey, "StorageClient"]

    @abstractmethod
    def __init__(self, config: StorageConfig):
        self.client: object
        self.config: StorageConfig
        ...

    # REQUIRED:

    @abstractmethod
    def get(self, key: ObjectKey) -> ObjectData:
        ...

    @abstractmethod
    def stat(self, key: StorageKey) -> Union[Object, Directory]:
        ...

    @abstractmethod
    def put(self, obj: Object, data: ObjectData) -> None:
        ...

    @abstractmethod
    def remove(self, key: StorageKey) -> None:
        ...

    @abstractmethod
    def list(self, prefix: DirectoryKey, recursive: bool = False) -> List[ObjectKey]:
        ...

    @property
    @abstractmethod
    def name(self) -> StorageClientKey:
        ...

    @property
    @abstractmethod
    def medium(self) -> Medium:
        ...

    # OPTIONAL:
    @abstractmethod
    def exists(self, key: StorageKey) -> bool:
        ...

    @abstractmethod
    def get_multiple(self, *keys: ObjectKey) -> List[ObjectData]:
        ...

    @abstractmethod
    def stat_multiple(self, *keys: StorageKey) -> List[Union[Object, Directory]]:
        ...

    @abstractmethod
    def put_multiple(self, *objects: Tuple[Object, ObjectData]) -> List[None]:
        ...

    @abstractmethod
    def remove_multiple(self, *keys: ObjectKey) -> List[None]:
        ...

    @abstractmethod
    def exists_multiple(self, *keys: ObjectKey) -> List[bool]:
        ...

    # MISCELLANEOUS:

    # Hash for ObjectStash client management set replacement
    @abstractmethod
    def __hash__(self):
        ...

    # String representation for pathing
    @abstractmethod
    def __repr__(self) -> str:
        ...
