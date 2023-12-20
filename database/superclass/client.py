"""Database model for the database service."""
from typing import Any, Dict, List, Optional

from typing_extensions import Self

from compute.interface.functions import FunctionClientInterface
from compute.models.functions.config import FunctionConfig
from database.interface.client import DatabaseInterface
from database.models.config import DatabaseConfig
from database.models.query import Query
from datamodel.data.model import Data
from datamodel.data.path import FieldPath
from repository.client.data import DataRepository
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey, StoragePath


class DatabaseClient(DatabaseInterface):
    def insert(self, key: str, value: Data) -> None:
        if key in self:
            raise KeyError(f"Key '{key}' already exists")
        self.data[key] = value

    def update(self, key: str, value: Data) -> None:
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        self.data[key] = value

    def remove(self, key: str) -> None:
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        del self.data[key]

    def get(self, key: str, default: Any = None) -> Optional[Data]:
        return self.data.get(key, default)

    def merge(self, key: str, head: Data, schema: Optional[Data]) -> None:
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        base = self.data[key]
        _, new = Data.merge(base, head, schema)
        self.insert(key, new)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def delete(self, key: str) -> None:
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        del self.data[key]

    def items(self, prefix: Optional[str] = None) -> List[str]:
        keys = [key for key in self.data.keys() if key.startswith(prefix)] if prefix else self.data.keys()
        return keys

    def query(self, query: Query) -> List[Data]:
        results = []
        for item in self.items():
            data = self.data[item]
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

        prefix: str = f"database/{name}"
        self.root: StorageKey = StorageKey(storage=storage.name, path=StoragePath(path=prefix))
        self.data: DataRepository = DataRepository(name=f"{prefix}/data", storage=storage)

        # Load config
        config_data = self.storage.get(self.root.join("._database.json"))
        self.config: DatabaseConfig = DatabaseConfig.from_raw(config_data)

        # Load operations
        self.operations: Dict[FieldPath, FunctionConfig] = self.config.operations
        if self.operations and not compute:
            raise ValueError("Database has calculated fields but no function client was provided")
        if compute:
            self.compute: FunctionClientInterface = compute
