"""
Sharded wrapper superclass.
"""
from storage.interface.client import StorageClientInterface
from storage.superclass.wrapper import StorageWrapper


# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object
class Sharded(StorageWrapper):
    def __init__(self, wrapped: StorageClientInterface):
        super().__init__(wrapped)
        raise NotImplementedError("Sharded storage strategy has not been implemented yet")
