"""Database model for the database service."""
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from typing_extensions import Self

from database.models.objects import JSON
from database.models.query import Query
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


# Might need upsert method
class DatabaseInterface(ABC):
    @abstractmethod
    def insert(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def update(self, key: str, value: JSON) -> None:
        ...

    @abstractmethod
    def remove(self, key: str) -> None:
        ...

    @abstractmethod
    def get(self, key: str) -> Any:
        pass

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def items(self) -> List[str]:
        pass

    @abstractmethod
    def query(self, query: Query) -> List[Any]:
        pass

    @abstractmethod
    def merge(self, key: str, head: Any, schema: Optional[Any]) -> None:
        pass

    @abstractmethod
    def namespace(self, name: str) -> Self:
        pass

    @abstractmethod
    def __init__(self, name: str, storage: StorageClientInterface):
        self.name: str
        self.storage: StorageClientInterface
        self.root: StorageKey
        self.data: StorageKey
        self.config: JSON
