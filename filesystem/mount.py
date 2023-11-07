"""Mount a StorageClient as a filesystem."""
from fuse import FUSE, LoggingMixIn, Operations

from storage.client.local import LocalClient
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey, StoragePath


class StorageOperations(LoggingMixIn, Operations):
    def __init__(self, storage: StorageClientInterface):
        self.storage: StorageClientInterface = storage
        self.root = StorageKey(storage=self.storage.name, path=StoragePath(path="filesystem/"))


if __name__ == "__main__":
    local_client = LocalClient(StoragePath(path="./local_data"))
    operations = StorageOperations(local_client)
    fuse = FUSE(operations, "/tmp/pioneer")
