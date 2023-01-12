from config.models.env import StorageConfig
from storage.base.client import BaseStorageClient
from storage.models.client.medium import Medium


class MemoryClient(BaseStorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
