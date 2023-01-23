from pathlib import PurePosixPath

from config.env import env
from role.interface.locking import LockInterface
from role.models.locking import State
from storage.interface.client import StorageClient
from storage.models.item.content import ObjectData
from storage.models.item.models import Object, ObjectKey


class Lock(LockInterface):
    def __init__(self, prefix: PurePosixPath, storage: StorageClient):
        self.prefix = prefix
        self.storage = storage
        self.state: State = State()
        self.path = self.prefix.joinpath(".lock")
        self.key = ObjectKey(storage.name, self.path)

    def acquire(self) -> None:
        if self.storage.exists(self.key):
            raise RuntimeError("Lock already exists")
        obj, data = Object.create(self.storage.name, self.path, self.state.to_bytes())
        self.storage.put(obj, data)

    def release(self) -> None:
        if self.storage.exists(self.key):
            lock: ObjectData = self.storage.get(self.key)
            state: State = State.parse_raw(lock.__root__)
            if state.cluster != env.cluster.name:
                raise RuntimeError("Lock is held by another cluster")
            self.storage.remove(self.key)

    def refresh(self) -> None:
        self.state = State()
        obj, data = Object.create(self.storage.name, self.path, self.state.to_bytes())
        self.storage.put(obj, data)

    def __enter__(self) -> "Lock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def __del__(self) -> None:
        self.release()
