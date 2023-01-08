from pysyncobj.batteries import replicated

from role.distribution import Distributed
from storage.models.client.model import StorageClient
from storage.models.item.data import ObjectData
from storage.models.item.models import Object
from storage.models.item.paths import ObjectKey
from storage.models.medium import Medium
from storage.models.wrapper import StorageWrapper

# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object


class Replicated(StorageWrapper, Distributed, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
        Distributed.__init__(self, f"Replicated({wrapped.name})", consumers=[])

    @replicated
    def put(self, obj: Object, data: ObjectData) -> None:
        if self.MEDIUM == Medium.LOCAL:
            return self.wrapped.put(obj, data)
        # Only pysyncobj master
        elif self.MEDIUM == Medium.REMOTE:
            return self.only_on_master(self.wrapped.put)(obj, data)
        else:
            return None

    def get(self, key: ObjectKey) -> ObjectData:
        self.doTick()
        return self.wrapped.get(key)
