"""
NoSQL database paradigm is a database that stores data in a document structure.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.interface.path import DirectoryKey


class NoSQL(Database):
    def __init__(self, storage: StorageClientInterface, name: DirectoryKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("NoSQL database has not been implemented yet")
