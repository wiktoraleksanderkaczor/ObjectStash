from copy import deepcopy
from datetime import datetime
from typing import List, Union

from pysyncobj.batteries import ReplDict, ReplLockManager, replicated

from ..utils.distribution import Distributed
from ..utils.env import env
from .storage import storage
from .validation import JSONish, Key


class ObjectLock(Distributed):
    def __init__(self, partition):
        self.locked = ReplLockManager(env["ACTIVITY"]["LOCK_TIMEOUT"], self.selfNode.address)
        Distributed.__init__(self, partition)


class PartitionLock(Distributed):
    def __init__(self, partition, fname=".lock"):
        self.partition = partition
        self.fname = self.partition + fname
        self.state = ReplDict()
        Distributed.__init__(self, self.partition, consumers=[self.state])

        if not self.state:
            self.state = self.check()
        if not self.state["obtained"]:
            self.lock()

    @replicated(sync=True)
    def set_lock(self, state: JSONish) -> JSONish:
        self.state = state
        return self.state

    def check(self) -> JSONish:
        state = (
            storage.get_object(self.fname)
            if storage.object_exists(self.fname)
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
                lockfile = storage.put_object(self.fname, state)
        # Handling if there is already a lock
        elif state["obtained"] and state["instance"] != Distributed.cluster_name:
            if not override:
                raise Exception("Partition is already locked by another client")
            # If override option is set
            state["obtained"] = True
            lockfile = storage.put_object(self.fname, state)

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
            lockfile = storage.put_object(self.fname, new)
        else:
            lockfile = storage.remove_object(self.fname)

        if not lockfile:
            raise Exception(f"Could not unlock for {self.partition} partition")
        self.set_lock(new)

    def __del__(self):
        is_last_node = len(self.otherNodes) == 0 and self.isReady()
        if self.state["obtained"] and is_last_node:  # and is last node
            self.unlock(env["ACTIVITY"]["LOCK_LEAVE"])


class PartitionMeta(Distributed):
    def __init__(self, partition: Key) -> None:
        self.partition = partition
        Distributed.__init__(self, self.partition)
        self.records: List[str] = []

    @replicated(sync=True)
    def add_record(self, record: str) -> None:
        self.records.append(record)

    @replicated(sync=True)
    def remove_record(self, record: str) -> None:
        self.records.remove(record)


class Partition:
    def insert(key: Key, value: JSONish) -> Key:
        return storage.put_object(key, value)

    def retrieve(self, keys: Union[Key, List[Key]]) -> JSONish:
        if isinstance(keys, Key):
            keys = [keys]
        keys = [self.prefix + key for key in keys]
        existing = [key for key in keys if key in self.meta.records]
        data = [storage.get_object(self.prefix + key) for key in existing]
        if len(data) != 1:
            return data
        return data[0]

    def exists(self, keys: Union[Key, List[Key]]) -> List[Key]:
        if isinstance(keys, str):
            keys = [keys]
        existing = [self.prefix + key if key in self.meta.records else None for key in keys]
        return existing

    def delete(self, keys: Union[Key, List[Key]]) -> List[bool]:
        existing = self.exists(keys)
        return storage.remove_objects(existing)

    def items(self) -> List[Key]:
        if not self.meta.records:
            objects = storage.list_objects(self.prefix)
            for obj in objects:
                self.meta.add_record(obj)
        return self.meta.records

    def __init__(self, name: Key, cached: bool = False):
        self.prefix = f"partitions/{name}"
        self.cached = cached
        self.lock = PartitionLock(self.prefix, ".lock")
        self.meta: PartitionMeta = PartitionMeta(self.prefix)
