from copy import deepcopy
import os

from ..storage import Capability, ObjectInfo, ObjectType, StorageClient
from ..validation import Key, JSONish

class LocalCLient(StorageClient):
    def __init__(
            self,
            container: str,
            region: str = None,
            secure: bool = True):
        super().__init__(container, region, secure)

    def create_container(self) -> bool:
        os.mkdir(self.container)
        return self.container_exists(self.container)

    def container_exists(self) -> bool:
        return os.path.isdir(self.container)

    def object_exists(self, key: Key) -> bool:
        return os.path.isfile(key)

    def get_object(self, key: Key) -> JSONish:
        with open(key, 'r') as infile:
            return JSONish(infile)
