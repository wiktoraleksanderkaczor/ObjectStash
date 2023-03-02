"""
Parameter database paradigm is a database that stores data in a one to one mapping between key and value.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class Parameter(Database):
    def __init__(self, storage: StorageClientInterface, name: StorageKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("Parameter database has not been implemented yet")
