import os
from typing import List

from storage.client.models.capabilities import Capability
from storage.client.models.client import StorageClient
from storage.client.models.objects import Object, ObjectID


class LocalClient(StorageClient):
    client_name: str = "Local"
    capabilities: List[Capability] = [Capability.BASIC]

    def __init__(self, container: str, region: str = None, secure: bool = True):
        super().__init__(container, region, secure)

    def create_container(self) -> bool:
        os.mkdir(self.container)
        return self.container_exists(self.container)

    def container_exists(self) -> bool:
        return os.path.isdir(self.container)

    def object_exists(self, key: ObjectID) -> bool:
        return os.path.isfile(key)

    def get_object(self, key: ObjectID) -> Object:
        with open(key, "r") as infile:
            return infile.read()
