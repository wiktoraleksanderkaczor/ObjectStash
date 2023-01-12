from storage.base.client import StorageClient
from storage.base.wrapper import StorageWrapper


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Sharded(StorageWrapper, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
