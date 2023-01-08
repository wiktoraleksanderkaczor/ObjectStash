from database.models.database import Database
from storage.models.client.model import StorageClient
from storage.models.item.paths import DirectoryKey


class Timeseries(Database):
    def __init__(self, storage: StorageClient, name: DirectoryKey) -> None:
        super().__init__(storage, name)
