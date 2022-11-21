from typing import List

from storage.client.models.capabilities import Capability
from storage.client.models.client import StorageClient
from storage.client.models.objects import Object, ObjectID


class MemoryClient(StorageClient):
    client_name: str = "Memory"
    capabilities: List[Capability] = [Capability.BASIC]

    def __init__(self, container: str, region: str = None, secure: bool = True):
        super().__init__(container, region, secure)

    def create_container(self) -> bool:
        pass

    def container_exists(self) -> bool:
        pass

    def object_exists(self, key: ObjectID) -> bool:
        pass

    def get_object(self, key: ObjectID) -> Object:
        pass
