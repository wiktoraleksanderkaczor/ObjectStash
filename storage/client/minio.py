from minio import Minio

from config.logger import log
from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.repository import Repository


class MinIOClient(StorageClient):
    def __init__(
        self,
        repository: Repository,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(repository)
        try:
            self.client = Minio(
                *args,
                **kwargs,
            )
        except Exception as e:
            log.exception(f"MinIO Exception [init]: {e}")
            raise e

    @property
    def medium(self) -> Medium:
        return Medium.REMOTE
