"""
Replicated storage wrapper
"""
from pysyncobj.batteries import replicated

from role.superclass.distribution import Distributed
from storage.interface.client import StorageClientInterface
from storage.interface.path import ObjectKey
from storage.models.client.medium import Medium
from storage.models.item.content import ObjectData
from storage.models.item.models import Object
from storage.superclass.wrapper import StorageWrapper

# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object


class Replicated(StorageWrapper, Distributed):
    def __init__(self, wrapped: StorageClientInterface):
        super().__init__(wrapped)
        Distributed.__init__(self, f"Replicated({wrapped.name})", consumers=[])

    @replicated
    def put(self, obj: Object, data: ObjectData) -> None:
        if self.MEDIUM == Medium.LOCAL:
            return self.wrapped.put(obj, data)
        # Only pysyncobj master
        if self.MEDIUM == Medium.REMOTE:
            return self.only_on_master(self.wrapped.put)(obj, data)

        return None

    def get(self, key: ObjectKey) -> ObjectData:
        self.doTick()
        return self.wrapped.get(key)
