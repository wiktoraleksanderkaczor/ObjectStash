"""Storage client interface."""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from config.models.env import StorageConfig
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.object import Object, ObjectData
from storage.models.object.path import StorageKey


class StorageClientInterface(ABC):
    initialized: Dict[StorageClientKey, "StorageClientInterface"]

    @abstractmethod
    def __init__(self, config: StorageConfig):
        self.client: object
        self.config: StorageConfig

    # REQUIRED:

    @abstractmethod
    def get(self, *key: StorageKey) -> ObjectData:
        ...

    @abstractmethod
    def stat(self, *key: StorageKey) -> Object:
        ...

    @abstractmethod
    def put(self, obj: Object, data: ObjectData) -> None:
        ...

    @abstractmethod
    def remove(self, *key: StorageKey) -> None:
        ...

    @abstractmethod
    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        ...

    @property
    @abstractmethod
    def name(self) -> StorageClientKey:
        ...

    @property
    @abstractmethod
    def medium(self) -> Medium:
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
