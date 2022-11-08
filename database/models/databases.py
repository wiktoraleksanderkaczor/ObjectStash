import json
from copy import deepcopy
from datetime import datetime
from io import BytesIO, StringIO
from typing import Any, Dict, List, Union, overload

from pysyncobj.batteries import ReplDict, ReplLockManager, replicated

from config.env import env
from database.merge import _merge_mapping
from database.models.merge import MergeIndex, MergeMode, MergeStrategy
from role.distribution import Distributed

# Need a way to make following some kind of default storage in config
from storage import clients
from storage.client.models.client import StorageClient
from storage.client.models.objects import ObjectID

storage: StorageClient = clients.get(env["STORAGE"]["CLIENT"])


class JSONish(dict):
    @overload
    def __init__(self, data: Union[Dict[str, Any], str, bytes, StringIO, BytesIO]):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, str):
            self.update(json.loads(data))
        elif isinstance(data, bytes):
            self.update(json.loads(data.decode()))
        elif isinstance(data, StringIO, BytesIO):
            self.update(json.loads(data.read()))

    def as_json(self):
        value: str = json.dumps(self, ensure_ascii=False, indent=env["DATA"]["JSON"]["INDENT"])
        value = value.encode(env["DATA"]["JSON"]["ENCODING"])
        return value

    def as_dict(self):
        return self

    def as_stringio(self):
        return StringIO(self.as_json())

    def as_bytesio(self):
        return BytesIO(self.as_json())

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            pass
        elif isinstance(v, str):
            v = json.loads(v)
        elif isinstance(v, StringIO):
            v = json.load(v)
        else:
            raise TypeError(f"Expected a dictionary, string or StringIO, not {type(v)}")
        invalid_keys = any([key for key in v.keys() if not isinstance(key, str)])
        if invalid_keys:
            raise ValueError("Data contains keys that are not valid")
        try:
            v = JSONish(v)
            v.as_json()
        except Exception:
            raise ValueError("Data is not JSON serializable")
        return v


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
    def __init__(self, partition: ObjectID) -> None:
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
    def insert(key: ObjectID, value: JSONish) -> ObjectID:
        return storage.put_object(key, value)

    def get(self, keys: Union[ObjectID, List[ObjectID]]) -> JSONish:
        if isinstance(keys, ObjectID):
            keys = [keys]
        keys = [self.prefix + key for key in keys]
        existing = [key for key in keys if key in self.meta.records]
        data = [storage.get_object(self.prefix + key) for key in existing]
        if len(data) != 1:
            return data
        return data[0]

    def exists(self, keys: Union[ObjectID, List[ObjectID]]) -> List[ObjectID]:
        if isinstance(keys, str):
            keys = [keys]
        existing = [self.prefix + key if key in self.meta.records else None for key in keys]
        return existing

    def delete(self, keys: Union[ObjectID, List[ObjectID]]) -> List[bool]:
        existing = self.exists(keys)
        return storage.remove_objects(existing)

    def items(self) -> List[ObjectID]:
        if not self.meta.records:
            objects = storage.list_objects(self.prefix)
            for obj in objects:
                self.meta.add_record(obj)
        return self.meta.records

    def merge_object(
        self,
        key: ObjectID,
        data: JSONish,
        index: MergeIndex = None,
        merge: MergeStrategy = None,
        mode: MergeMode = MergeMode.UPDATE,
    ) -> bool:
        old = self.retrieve(key)
        new = _merge_mapping(old, data, index, merge, mode)
        return self.insert(key, new)

    def __init__(self, name: ObjectID, cached: bool = False):
        self.prefix = f"partitions/{name}"
        self.cached = cached
        self.lock = PartitionLock(self.prefix, ".lock")
        self.meta: PartitionMeta = PartitionMeta(self.prefix)


class Schema(Partition):
    def __init__(self) -> None:
        self.fname: str = "schema.json"
        self.schema: Dict[str, str] = None
        if storage.object_exists(self.fname):
            self.schema = storage.get_object(self.fname)
        else:
            self.schema = {}
            storage.put_object(self.fname, self.schema)


class Table(Partition):
    def __init__(self, name: str):
        super().__init__(name)

    def select_by_value(val: dict):
        pass
