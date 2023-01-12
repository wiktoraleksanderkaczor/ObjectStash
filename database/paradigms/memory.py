from database.models.database import Database
from storage.interface.client import StorageClient
from storage.interface.path import DirectoryKey


class Memory(Database):
    def __init__(self, storage: StorageClient, name: DirectoryKey) -> None:
        super().__init__(storage, name)
