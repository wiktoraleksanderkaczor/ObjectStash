"""Database model for the database service."""
from typing import Callable, List, Optional

from typing_extensions import Self
from database.interface.client import DatabaseInterface
from database.models.objects import JSON
from storage.interface.client import StorageClientInterface
from storage.models.object.content import ObjectContentInfo, ObjectData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath


class DatabaseClient(DatabaseInterface):
    def insert(self, key: str, value: JSON) -> None:
        path = self.data.join(key)
        json = value.json()
        encoded = json.encode("utf-8")
        data = ObjectData(__root__=encoded)
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=path, content=content)
        self.storage.put(obj, data)

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

    def select(self, condition: Callable[[JSON], bool]) -> List[JSON]:
        records = [self.get(key) for key in self.items()]
        records = list(filter(condition, records))
        return records

    def namespace(self, name: str) -> Self:
        """
        Create a new namespace in the database.

        Args:
            name (str): Name of the namespace.
            Multiple can be specified with separators.

        Returns:
            Self: A new database client of same type.
        """
        return self.__class__(self.storage, self.data.join(name))

    def __init__(self, storage: StorageClientInterface, name: StorageKey):
        self.storage: StorageClientInterface = storage
        self.root: StorageKey = StorageKey(storage=storage.name, path=StoragePath(f"database/{name.path}"))
        self.data: StorageKey = self.root.join("data")
