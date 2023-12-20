"""Index wrapper for database client."""
from typing import List, Optional

from database.models.query import Query
from database.superclass.client import DatabaseClient
from database.wrapper.interface import DatabaseWrapper
from datamodel.data.model import Data


class IndexEntry(Data):
    references: List[str] = []


class IndexWrapper(DatabaseWrapper):
    def __init__(self, wrapped: DatabaseClient, storage: DatabaseClient):
        super().__init__(wrapped)
        self.index: DatabaseClient = storage

    def insert(self, key: str, value: Data) -> None:
        for k, _ in value.flattened:
            ckey = repr(k)
            if ckey in self.index:
                data = self.index.get(ckey)
                entry: IndexEntry = IndexEntry.from_obj(data) if data else IndexEntry(references=[])
                entry.references.append(key)
                self.index.insert(ckey, entry)
        return super().insert(key, value)

    def query(self, query: Query) -> List[Optional[Data]]:
        collections = [self.index.get(repr(field)) for field in query.outputs]
        items = [collection for collection in collections if collection]
        keys = [IndexEntry.from_obj(item).references for item in items]
        unwrapped = [item for sublist in keys for item in sublist]
        data = [self.__wrapped__.get(item) for item in unwrapped]
        data = [item for item in data if query(item)]
        return data
