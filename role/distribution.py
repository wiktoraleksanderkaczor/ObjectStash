from typing import List

from pysyncobj.batteries import replicated

from config.discovery import host_ip, port
from config.env import env
from config.logger import log

from ..config.env import env
from ..config.logger import log


class Distributed(SyncObj):
    # Peer data structure
    cluster_name = env.cluster.name
    peers: List[str] = env.cluster.initial_peers
    distributed_objects: List["Distributed"] = []

    def __init__(self, name: str, consumers: List[str] = None):
        if not consumers:
            consumers = []
        SyncObj.__init__(self, f"{host_ip}:{port}", Distributed.peers, consumers=consumers)
        Distributed.distributed_objects.append(self)
        while not self.isReady():
            log.debug(f"Waiting to acquire initial data for {name}...")
        self.waitReady()

    # Check if master node
    def is_master(self):
        return self.getStatus()["leader"] == self.selfNode

    # Only execute on master raft node (pysyncobj) decorator
    def only_on_master(self, func):
        def wrapper(*args, **kwargs):
            if self.is_master():
                return func(*args, **kwargs)
            else:
                return lambda *args, **kwargs: None

        return wrapper

    def is_synced(self) -> bool:
        status = self.getStatus()
        return status["leader_commit_idx"] == status["commit_idx"]

    def local_sync(self):
        while not self.is_synced():
            self.waitReady()
            self.doTick()

    @replicated
    def global_sync(self):
        self.local_sync()
