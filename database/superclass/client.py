"""Database model for the database service."""
from typing import Dict, List, Optional

from typing_extensions import Self

from compute.interface.functions import FunctionClientInterface
from compute.models.functions.config import FunctionConfig
from database.interface.client import DatabaseInterface
from database.models.config import DatabaseConfig
from database.models.query import Query
from datamodel.data import JSON, FieldPath
from storage.interface.client import StorageClientInterface
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath


class DatabaseClient(DatabaseInterface):
    def insert(self, key: str, value: JSON) -> None:
        path = self.data.join(key)
        json = value.json()
        encoded = json.encode("utf-8")
        obj, data = Object.create_file(path, encoded)
        self.storage.put(obj, data)

    def update(self, key: str, value: JSON) -> None:
        self.remove(key)
        self.insert(key, value)

    def remove(self, key: str) -> None:
        path = self.data.join(key)
        self.storage.remove(path)

    def get(self, key: str) -> JSON:
        path = self.data.join(key)
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(path).__root__
        return JSON.parse_raw(data)

    def merge(self, key: str, head: JSON, schema: Optional[JSON]) -> None:
        base = self.get(key)
        _, new = JSON.merge(base, head, schema)
        self.insert(key, new)

    def __contains__(self, key: str) -> bool:
        path = self.data.join(key)
        return path in self.storage

    def delete(self, key: str) -> None:
        path = self.data.join(key)
        if key in self:
            self.storage.remove(path)

    def items(self, prefix: Optional[str] = None) -> List[str]:
        path = self.data.join(prefix) if prefix else self.data
        return [item.path.name for item in self.storage.list(path)]

    def query(self, query: Query) -> List[JSON]:
        results = []
        for item in self.items():
            data = self.get(item)
            if query(data):
                results.extend(data)
        return results

    def namespace(self, name: str) -> Self:
        """
        Create a new namespace in the database.

        Args:
            name (str): Name of the namespace.
            Multiple can be specified with separators.

        Returns:
            Self: A new database client of same type.
        """
        return self.__class__(f"{self.name}/{name}", self.storage)

    def __init__(self, name: str, storage: StorageClientInterface, compute: Optional[FunctionClientInterface] = None):
        self.name: str = name
        self.storage: StorageClientInterface = storage
        self.root: StorageKey = StorageKey(storage=storage.name, path=StoragePath(f"database/{name}"))
        self.data: StorageKey = self.root.join("data")

        # Load config
        config_data = self.storage.get(self.root.join("config.json")).__root__
        self.config: DatabaseConfig = DatabaseConfig.parse_raw(config_data)

        # Load operations
        self.operations: Dict[FieldPath, FunctionConfig] = self.config.operations
        if self.operations and not compute:
            raise ValueError("Database has calculated fields but no function client was provided")
        if compute:
            self.compute: FunctionClientInterface = compute
