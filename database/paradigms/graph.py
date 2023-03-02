"""
Graph database paradigm is a database that stores data in a graph structure.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class Graph(Database):
    def __init__(self, storage: StorageClientInterface, name: StorageKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("Graph database has not been implemented yet")
