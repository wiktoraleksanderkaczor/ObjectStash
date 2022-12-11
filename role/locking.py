from datetime import datetime

from pydantic import Protocol

from config.env import env
from role.distribution import Distributed
from role.models.locking import State
from storage.models.client import StorageClient
from storage.models.objects import Object, ObjectID


class Lock(Protocol):
    def lock(self):
        if self.valid():
            return

        state = self.new()
        obj = Object(name=self.path, data=state)
        if not self.storage.put_object(obj):
            raise Exception(f"Cannot make lock file in {self.path}")
        if not self.valid():
            raise Exception(f"Created lock file in {self.path} is not valid")
        self.state = state

    def unlock(self):
        return self.storage.remove_object(self.path)

    def exists(self) -> State:
        return self.storage.object_exists(self.path)

    def new(self):
        return State(
            duration=env.storage[self.storage.name].locking.duration,
        )

    def valid(self) -> bool:
        # Not locked
        if not self.exists():
            return False

        self.state = self.storage.get_object(self.path)
        # Lock is not for current cluster
        if self.state.cluster != env.cluster.name:
            return False
        # Lock expired
        if datetime.utcnow() < self.state.timestamp + self.state.duration:
            return False
        # All checks out
        return True

    def __init__(self, storage: StorageClient, prefix: ObjectID):
        self.storage = storage
        fname = env.storage[storage.name].locking.filename
        self.path = prefix.joinpath(fname)
        self.state: State = None


class DistributedLock(Lock, Distributed):
    def __init__(self, storage: StorageClient, prefix: ObjectID):
        super().__init__(storage, prefix)
        Distributed.__init__(self, ":".join(storage.name, prefix), consumers=[self.state])

    def __del__(self):
        is_last_node = len(self.otherNodes) == 0 and self.isReady()
        if self.state and is_last_node:  # and is last node
            self.unlock()
        return super().__del__()
