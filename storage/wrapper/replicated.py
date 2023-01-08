from pysyncobj.batteries import replicated

from role.distribution import Distributed
from storage.models.client.model import StorageClient
from storage.models.item.models import Object
from storage.models.item.paths import StorageKey
from storage.models.medium import Medium
from storage.models.wrapper import StorageWrapper

# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object


class Replicated(StorageWrapper, Distributed, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
        Distributed.__init__(self, f"Replicated({wrapped.name})", consumers=[])

    @replicated
    def put_object(self, obj: Object) -> bool:
        if self.MEDIUM == Medium.LOCAL:
            return self.wrapped.put_object(obj)
        # Only pysyncobj master
        elif self.MEDIUM == Medium.REMOTE:
            return self.only_on_master(self.wrapped.put_object)(obj)
        else:
            return False

    def get_object(self, key: StorageKey) -> Object:
        self.doTick()
        return self.wrapped.get_object(key)
