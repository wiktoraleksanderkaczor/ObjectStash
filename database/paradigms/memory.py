"""
Memory is a database that stores all data in memory. It is not persistent.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class Memory(Database):
    def __init__(self, storage: StorageClientInterface, name: StorageKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("Memory database has not been implemented yet")
