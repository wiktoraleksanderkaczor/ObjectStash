"""
Locking for objects in storage backend (S3, Azure, etc.) and cache backend (Redis, Memcached, etc.) to prevent
concurrent access to the same object. This is done by creating a lock file in the storage backend and cache backend
and checking if the lock file is still valid before performing the action. If the lock file is not valid, the lock
file is removed and the action is performed. If the lock file is still valid, the action is not performed and an
exception is raised.

Must be accessible via 'with' statement.
See https://docs.python.org/3/reference/datamodel.html#context-managers

Separate option for record locking needed... something in-memory, not in storage backend.
"""

# from datetime import datetime

# from config.env import env
# from role.distribution import Distributed
# from role.models.locking import State
# from storage.models.client import StorageClient
# from storage.models.objects import Object, ObjectID


# class Lock:
#     def lock(self):
#         if self.valid():
#             return

#         state = self.new()
#         obj = Object(name=self.path, data=state)
#         if not self.storage.put_object(obj):
#             raise Exception(f"Cannot make lock file in {self.path}")
#         if not self.valid():
#             raise Exception(f"Created lock file in {self.path} is not valid")
#         self.state = state

#     def unlock(self):
#         return self.storage.remove_object(self.path)

#     def exists(self) -> State:
#         return self.storage.object_exists(self.path)

#     def new(self):
#         return State(
#             duration=env.storage[self.storage.name].locking.duration,
#         )

#     def valid(self) -> bool:
#         # Not locked
#         if not self.exists():
#             return False

#         self.state = self.storage.get_object(self.path)
#         # Lock is not for current cluster
#         if self.state.cluster != env.cluster.name:
#             return False
#         # Lock expired
#         if datetime.utcnow() < self.state.timestamp + self.state.duration:
#             return False
#         # All checks out
#         return True

#     def __init__(self, storage: StorageClient, prefix: ObjectID):
#         self.storage = storage
#         fname = env.storage[storage.name].locking.filename
#         self.path = prefix.joinpath(fname)
#         self.state: State = None

#     def __enter__(self):
#         self.lock()
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.unlock()
#         return False


# class DistributedLock(Lock, Distributed):
#     def __init__(self, storage: StorageClient, prefix: ObjectID):
#         super().__init__(storage, prefix)

#         Distributed.__init__(self, ":".join(storage.name, prefix), consumers=[self.state])

#     def __del__(self):
#         is_last_node = len(self.otherNodes) == 0 and self.isReady()
#         if self.state and is_last_node:  # and is last node
#             self.unlock()
#         del self


# # Lock for records in database using pysyncobj (distributed)
# class RecordLock(DistributedLock):

#     # Lock for record
#     def lock(self, record):
#         if self.valid():
#             return

#         state = self.new()
#         state.record = record
#         obj = Object(name=self.path, data=state)
#         if not self.storage.put_object(obj):
#             raise Exception(f"Cannot make lock file in {self.path}")
#         if not self.valid():
#             raise Exception(f"Created lock file in {self.path} is not valid")
#         self.state = state
