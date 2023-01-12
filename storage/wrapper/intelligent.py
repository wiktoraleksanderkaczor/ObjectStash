"""
    An intelligent tiering system between data volume, access and durability needs, some mesh of replica and sharding
"""
from storage.base.wrapper import StorageWrapper
from storage.interface.client import StorageClient


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Intelligent(StorageWrapper, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
        raise NotImplementedError("Intelligent storage strategy has not been implemented yet")
