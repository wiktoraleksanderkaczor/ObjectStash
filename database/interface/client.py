"""Database model for the database service."""
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from typing_extensions import Self

from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class DatabaseInterface(ABC):
    @abstractmethod
    def insert(self, key: str, value: Any) -> None:
        pass

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
    def select(self, condition: Callable[[Any], bool]) -> List[Any]:
        pass

    @abstractmethod
    def merge(self, key: str, head: Any, schema: Optional[Any]) -> None:
        pass

    @abstractmethod
    def namespace(self, name: str) -> Self:
        pass

    @abstractmethod
    def __init__(self, storage: StorageClientInterface, name: StorageKey):
        self.storage: StorageClientInterface
        self.root: StorageKey
        self.data: StorageKey
