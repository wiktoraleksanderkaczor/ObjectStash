"""
Graph database paradigm is a database that stores data in a graph structure.
"""
from database.superclass.client import DatabaseClient
from storage.interface.client import StorageClientInterface


class Graph(DatabaseClient):
    def __init__(self, name: str, storage: StorageClientInterface) -> None:
        super().__init__(name, storage)
        raise NotImplementedError("Graph database has not been implemented yet")
