from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.repository import Repository


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
