from pysyncobj.batteries import replicated

from role.distribution import Distributed
from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.objects import Object, ObjectID
from storage.models.wrapper import StorageWrapper

# Methods with multiple MUST be overwritten, i.e. multi_get() otherwise, it'll fall to the wrapped object


class Replicated(StorageWrapper, Distributed, StorageClient):
    def __init__(self, wrapped: StorageClient):
        super().__init__(wrapped)
        Distributed.__init__(self, f"Replicated:{wrapped.CLIENT_NAME}", consumers=[])

    @replicated
    def put_object(self, obj: Object) -> bool:
        if self.MEDIUM == Medium.LOCAL:
            return self.wrapped.put_object(obj)
        # Only pysyncobj master
        elif self.MEDIUM == Medium.REMOTE:
            return self.only_on_master(self.wrapped.put_object)(obj)
        else:
            return False

    def get_object(self, key: ObjectID) -> Object:
        self.doTick()
        return self.wrapped.get_object(key)
