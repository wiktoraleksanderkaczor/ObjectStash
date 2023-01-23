from abc import ABC, abstractmethod
from typing import Callable, List

from pydantic import AnyUrl
from pysyncobj import SyncObjConf, SyncObjConsumer
from pysyncobj.batteries import replicated


class DistributedInterface(ABC):
    # Peer data structure
    cluster_name: str
    peers: List[AnyUrl]
    distributed_objects: List["DistributedInterface"]
    syncobj_conf: SyncObjConf

    @abstractmethod
    def __init__(self, name: str, consumers: List[SyncObjConsumer]):
        ...

    # Check if master node
    @abstractmethod
    def is_master(self) -> bool:
        ...

    # Only execute on master raft node (pysyncobj) decorator
    @replicated
    @abstractmethod
    def only_on_master(self, func) -> Callable:
        ...

    @abstractmethod
    def is_synced(self) -> bool:
        ...

    @abstractmethod
    def local_sync(self):
        ...

    @replicated
    @abstractmethod
    def global_sync(self):
        ...
