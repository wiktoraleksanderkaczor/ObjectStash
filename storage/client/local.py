import os
from typing import List

from storage.models.capabilities import Capability
from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.objects import Object, ObjectID


class LocalClient(StorageClient):
    CLIENT_NAME: str = "Local"
    CAPABILITIES: List[Capability] = [Capability.BASIC]
    MEDIUM: str = Medium.LOCAL

    def __init__(
        self,
        container: str,
        *args,
        **kwargs,
    ):
        super().__init__(container)

    def put_container(self) -> bool:
        os.mkdir(self.container)
        return self.head_container()

    def head_container(self) -> bool:
        return os.path.isdir(self.container)

    def object_exists(self, key: ObjectID) -> bool:
        return os.path.isfile(key)

    def get_object(self, key: ObjectID) -> Object:
        with open(key, "r") as infile:
            return infile.read()
