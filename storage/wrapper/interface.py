"""
Interface for storage wrapper.
"""
from typing import List

from pysyncobj import SyncObjConsumer

from role.superclass.wrapping import DistributedObjectProxy
from storage.interface.client import StorageClientInterface


class StorageWrapper(DistributedObjectProxy):
    def __init__(self, wrapped: StorageClientInterface, consumers: List[SyncObjConsumer]):
        super().__init__(wrapped, consumers)
        self.__wrapped__: StorageClientInterface = wrapped  # typing fix

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__wrapped__.__repr__()})"
