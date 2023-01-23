"""Memory client for storage."""
from config.models.env import StorageConfig
from storage.models.client.medium import Medium
from storage.superclass.client import BaseStorageClient


class MemoryClient(BaseStorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        raise NotImplementedError("Memory client has not been implemented yet")

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
