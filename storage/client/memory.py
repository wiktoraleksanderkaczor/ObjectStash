from storage.base.client import StorageClient
from storage.models.client.medium import Medium
from storage.models.client.repository import Repository


class MemoryClient(StorageClient):
    def __init__(
        self,
        repository: Repository,
        *args,
        **kwargs,
    ):
        super().__init__(repository)

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
