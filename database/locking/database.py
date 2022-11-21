from copy import deepcopy
from datetime import datetime

from pysyncobj.batteries import replicated

from config.env import env
from database.models.locking import Lock
from database.models.objects import JSONish
from role.distribution import Distributed
from storage.client.models.client import StorageClient


class DatabaseLock(Distributed, Lock):
    def __init__(self, storage: StorageClient, partition, fname=".lock"):
        Lock.__init__(self, partition, storage, fname)
        Distributed.__init__(self, self.partition, consumers=[self.state])

    @replicated(sync=True)
    def set_lock(self, state: JSONish) -> JSONish:
        self.state = state
        return self.state

    def check(self) -> JSONish:
        state = (
            self.storage.get_object(self.fname)
            if self.storage.object_exists(self.fname)
            else {"isotime": datetime.utcnow().isoformat(), "instance": Distributed.cluster_name, "obtained": False}
        )
        return state

    def lock(self, override: bool = False) -> bool:
        # Check if lock is currently obtained
        if self.state["instance"] == Distributed.cluster_name and self.state["obtained"]:
            return True

        # Get current lock or possible new lock
        state = self.check()
        lockfile = None
        if not state["obtained"]:
            state["obtained"] = True
            if state["instance"] == Distributed.cluster_name:
                lockfile = self.storage.put_object(self.fname, state)
        # Handling if there is already a lock
        elif state["obtained"] and state["instance"] != Distributed.cluster_name:
            if not override:
                raise Exception("Partition is already locked by another client")
            # If override option is set
            state["obtained"] = True
            lockfile = self.storage.put_object(self.fname, state)

        if not lockfile:
            raise Exception(f"Could not acquire lock for {self.partition} partition")

        # Check whether lock in remote is as local
        remote = self.check()
        if remote != state:
            raise Exception("Different lock was obtained during locking")

        self.set_lock(state)
        return True

    def unlock(self, leave: bool = env["ACTIVITY"]["LOCK_LEAVE"]):
        new = deepcopy(self.state)
        new["obtained"] = False
        lockfile = None
        if leave:
            lockfile = self.storage.put_object(self.fname, new)
        else:
            lockfile = self.storage.remove_object(self.fname)

        if not lockfile:
            raise Exception(f"Could not unlock for {self.partition} partition")
        self.set_lock(new)

    def __del__(self):
        is_last_node = len(self.otherNodes) == 0 and self.isReady()
        if self.state["obtained"] and is_last_node:  # and is last node
            self.unlock(env["ACTIVITY"]["LOCK_LEAVE"])
