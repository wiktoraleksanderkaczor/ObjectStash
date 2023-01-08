from database.models.database import Database
from storage.models.client.model import StorageClient
from storage.models.item.paths import StorageKey


class Relational(Database):
    def __init__(self, storage: StorageClient, name: StorageKey) -> None:
        super().__init__(storage, name)
