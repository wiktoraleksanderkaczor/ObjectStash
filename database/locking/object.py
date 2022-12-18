# from pysyncobj.batteries import ReplLockManager

# from config.env import env

# # from database.models.locking import Lock
# from role.distribution import Distributed

# class RecordLockManager(Distributed):
#     def __init__(self, partition):
#         self.lock_manager = ReplLockManager(
#             self,
#             autoUnlockTime=env.records.autounlock.seconds,
#             selfID=self.selfNode.address,
#         )
#         Distributed.__init__(self, partition, consumers=[self.lock_manager])
#         self.locked = []

#     def __enter__(self, record: str):
#         acquired = self.lock_manager.tryAcquire(record, sync=True)
#         if acquired:
#             self.locked.append(record)
#         return acquired

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         for i in self.locked:
#             self.lock_manager.release(i)
