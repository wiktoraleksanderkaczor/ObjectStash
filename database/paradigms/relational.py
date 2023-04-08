"""
Relational database paradigm is a database that stores data in a relational table structure.
"""
from database.superclass.client import DatabaseClient
from storage.interface.client import StorageClientInterface


class Relational(DatabaseClient):
    def __init__(self, name: str, storage: StorageClientInterface) -> None:
        super().__init__(name, storage)
        raise NotImplementedError("Relational database has not been implemented yet")
