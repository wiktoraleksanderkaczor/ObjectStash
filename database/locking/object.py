from pysyncobj.batteries import ReplLockManager

from config.env import env
from database.models.locking import Lock
from role.distribution import Distributed


class ObjectLock(Distributed, Lock):
    def __init__(self, partition):
        self.locked = ReplLockManager(env["ACTIVITY"]["LOCK_TIMEOUT"], self.selfNode.address)
        Distributed.__init__(self, partition)
