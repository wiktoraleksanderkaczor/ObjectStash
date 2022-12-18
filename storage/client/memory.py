from typing import List

from storage.models.capabilities import Capability
from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.objects import Object, ObjectID


class MemoryClient(StorageClient):
    CLIENT_NAME: str = "Memory"
    CAPABILITIES: List[Capability] = [Capability.BASIC]
    MEDIUM: str = Medium.LOCAL

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
