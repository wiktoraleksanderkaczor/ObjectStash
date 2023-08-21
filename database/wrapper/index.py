"""Index wrapper for database client."""
from typing import List

from pysyncobj import SyncObjConsumer

from database.models.query import Query
from database.superclass.client import DatabaseClient
from database.wrapper.interface import DatabaseWrapper
from datamodel.data import JSON


class IndexWrapper(DatabaseWrapper):
    def __init__(self, wrapped: DatabaseClient, storage: DatabaseClient, consumers: List[SyncObjConsumer]):
        super().__init__(wrapped, consumers)
        self.index: DatabaseClient = storage

    def insert(self, key: str, value: JSON) -> None:
        flattened = value.flatten()
        for item in flattened:
            k, v = item
            self.index.insert(repr(k), v)
        return super().insert(key, value)

    def query(self, query: Query) -> List[JSON]:
        collections = [self.index.items(repr(field)) for field in query.outputs]
        items = [item for collection in collections for item in collection]
        data = [super().get(item) for item in items]
        data = list(filter(query, data))
        return data
