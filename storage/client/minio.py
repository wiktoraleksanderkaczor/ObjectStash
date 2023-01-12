from minio import Minio

from config.logger import log
from config.models.env import StorageConfig
from storage.base.client import BaseStorageClient
from storage.models.client.medium import Medium


class MinIOClient(BaseStorageClient):
    def __init__(self, config: StorageConfig) -> None:
        super().__init__(config)
        try:
            self.client = Minio(
                config.endpoint, config.access_key, config.secret_key, secure=config.secure, region=config.region
            )
        except Exception as e:
            log.exception(f"MinIO Exception [init]: {e}")
            raise e

    @property
    def medium(self) -> Medium:
        return Medium.REMOTE
