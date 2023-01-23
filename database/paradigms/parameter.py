"""
Parameter database paradigm is a database that stores data in a one to one mapping between key and value.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.interface.path import DirectoryKey


class Parameter(Database):
    def __init__(self, storage: StorageClientInterface, name: DirectoryKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("Parameter database has not been implemented yet")
