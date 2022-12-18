"""
    An intelligent tiering system between data volume, access and durability needs, some mesh of replica and sharding
"""
from storage.models.client import StorageClient
from storage.models.wrapper import StorageWrapper


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Intelligent(StorageWrapper, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
