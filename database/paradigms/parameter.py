from database.models.database import Database
from storage.base.client import StorageClient
from storage.interface.path import DirectoryKey


class Parameter(Database):
    def __init__(self, storage: StorageClient, name: DirectoryKey) -> None:
        super().__init__(storage, name)
