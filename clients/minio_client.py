from io import BytesIO
from pathlib import PurePath as Path
from typing import List

from minio import Minio

from ..models.exceptions import StorageError
from ..models.objects import ObjectInfo
from ..models.storage import Capability, StorageClient
from ..models.validation import JSONish, Key
from ..utils.env import env
from ..utils.logger import log


class MinioClient(StorageClient):
    client_name: str = "MinIO"
    capabilities: List[Capability] = [Capability.BASIC]

    def __init__(self, container: str, region: str = None, secure: bool = True) -> None:
        super().__init__(container, region, secure)
        try:
            self.client = Minio(
                env, access_key=self.access_key, secret_key=self.secret_key, region=self.region, secure=self.secure
            )
        except Exception as e:
            err = StorageError(e)
            log.exception(f"MinIO Exception [init]: {err}")
            raise err

    def object_exists(self, key: Key) -> bool:
        prefix = key.rsplit("/", 1)[-1] if "/" in key else None
        return key in self.client.list_objects(self.container, prefix)

    def container_exists(self) -> bool:
        return self.client.bucket_exists(self.container)

    def create_container(self) -> bool:
        self.client.make_bucket(self.container)

    def list_objects(self, prefix: Key, recursive: bool = False) -> List[str]:
        return self.client.list_objects(self.container, prefix, recursive)

    def put_object(self, key: Key, data: JSONish) -> str:
        data = BytesIO(data)
        return self.client.put_object(self.container, key, data)

    # TODO: Fix this thing, set up a ObjectInfo structure that will work between all storage
    # Likely need an Object option too... with the data. It'll need to be
    # compatible with JSONish
    def stat_object(self, key: str) -> ObjectInfo:
        data = self.client.stat_object(self.container, key)

        return self.client.stat_object(self.container, key).__dict__
