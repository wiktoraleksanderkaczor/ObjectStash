from config.models.env import StorageConfig
from storage.base.client import StorageClient
from storage.models.client.medium import Medium


class LocalClient(StorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
