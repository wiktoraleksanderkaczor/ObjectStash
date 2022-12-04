import json

from pysyncobj.batteries import replicated

from config.env import env
from database.models.locking import Lock
from database.models.objects import JSONish
from role.distribution import Distributed
from storage.models.client import StorageClient
from storage.models.objects import Object


class DatabaseLock(Distributed, Lock):
    def __init__(self, storage: StorageClient, partition):

        Lock.__init__(self, partition, storage, env.storage[storage.name].filename.lock)
        Distributed.__init__(self, self.partition, consumers=[self.state])

    @replicated(sync=True)
    def set_lock(self, state: JSONish) -> JSONish:
        self.state = state
        return self.state

    def check(self) -> JSONish:
        state = self.storage.get_object(self.fname) if self.storage.object_exists(self.fname) else self.new()
        return state

    def lock(self) -> bool:
        # Check if lock is currently obtained
        if self.state["instance"] == Distributed.cluster_name and self.state["obtained"]:
            return True

        # Get current lock or possible new lock
        state = self.check()
        locked = None
        locker = Object(name=self.fname, data=json.dumps(state))
        if not state["obtained"]:
            state["obtained"] = True
            if state["instance"] == Distributed.cluster_name:
                locked = self.storage.put_object(locker)
        # Handling if there is already a lock
        elif state["obtained"] and state["instance"] != Distributed.cluster_name:
            raise Exception("Partition is already locked by another client")

        if not locked:
            raise Exception(f"Could not acquire lock for {self.partition} partition")

        # Check whether lock in remote is as local
        remote = self.check()
        if remote != state:
            raise Exception("Different lock was obtained during locking")

        self.set_lock(state)
        return True

    def unlock(self) -> bool:
        if self.storage.object_exists(self.fname):
            return self.storage.remove_object(self.fname)
        return True

    def __del__(self):
        is_last_node = len(self.otherNodes) == 0 and self.isReady()
        if self.state["obtained"] and is_last_node:  # and is last node
            self.unlock()
