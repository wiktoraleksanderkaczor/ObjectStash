"""Local storage client."""
from config.models.env import StorageConfig
from storage.models.client.medium import Medium
from storage.superclass.client import BaseStorageClient


class LocalClient(BaseStorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        raise NotImplementedError("Local client has not been implemented yet")

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
