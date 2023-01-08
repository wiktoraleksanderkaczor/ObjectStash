from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from config.env import env
from role.scheduling import scheduler
from storage.models.client.model import StorageClient
from storage.models.item.paths import StorageKey


class LockState(BaseModel):
    cluster: str = env.cluster.name
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration: timedelta = env.locking.duration


# class StorageLock:
#     def __init__(self, storage: StorageClient, path: ObjectID) -> None:
#         self.storage = storage
#         self.path = path ->

#     def new(self):
#         return StorageLockState(
#             duration=env.storage[self.storage.CLIENT_NAME].locking.duration,
#         )

#     def release(self):
#         return self.storage.remove_object(self.path)

#     def acquire(self):
#         exists = self.storage.object_exists(self.path)
#         state = (
#               self.storage.get_object(self.path) if exists else self.new()
#         )
#         obj = Object(name=self.path, data=state)
#         if not self.storage.put_object(obj):
#             raise Exception(f"Cannot make lock file in {self.path}")
#         if not self.valid():
#             raise Exception(f"Created lock file in {self.path} is not valid")
#         self.state = state


# if __name__ == "__main__":
#     a = bytes(StorageLockState(duration=60).json().encode("utf-8"))
#     print(a)


# class StorageLockV2:
#     def __init__(self, name: str, storage: StorageClient, path: ObjectID) -> None:
#         self.name = name
#         self.storage = storage
#         self.path = pat ->h

#     def get_lock(self) -> StorageLockState:
#         obj = self.storage.get_object(self.path)
#         return StorageLockState(obj)

#     def release_lock(self, key: str):
#         self.storage.remove_object(self.path)

#     def new_lock(self, key: str):
#         return StorageLockState(
#             cluster=env.cluster.name,
#             timestamp=datetime.utcnow(),
#             duration=env.storage[self.storage.CLIENT_NAME].locking.duration,
#         )

#     def create_lock(self, key: str):
#         obj = self.new_lock(key)
#         self.storage.put_object(obj)
#         return obj

#     def acquire_lock(self, key: str):
#         obj = self.create_lock(key)
#         if not self.valid_lock(obj):
#             raise Exception(f"Created lock file in {key} is not valid")
#         return obj

#     # Validate lock:
#     def valid_lock(self, obj: StorageLockState) -> bool:
#         # Not locked
#         if not obj:
#             return False

#         # Lock is not for current cluster
#         if obj.cluster != env.cluster.name:
#             return False

#         # Lock expired
#         if datetime.utcnow() < obj.timestamp + timedelta(seconds=obj.duration):
#             return False

#         # All checks out
#         return True


class Lock:
    def __init__(self, name: str, storage: StorageClient, path: StorageKey) -> None:
        self.name = name
        self.storage = storage
        self.path = path
        self.acquire()
        interval = env.locking.duration - env.locking.grace
        scheduler.every(interval.seconds).seconds.do(self.refresh)

    def acquire(self) -> None:
        ...

    def release(self) -> None:
        ...

    def refresh(self) -> None:
        ...
