from io import BytesIO
from typing import Any, Dict, List

from minio import Minio

from ..env import env
from ..exceptions import StorageError
from ..logger import log
from ..storage import Capability, ObjectInfo, ObjectType, StorageClient
from ..validation import JSONish, Key, PrefixPath


class MinioClient(StorageClient):
    client_name: str = "MinIO"
    capabilities: List[Capability] = [Capability.BASIC]

    def __init__(
            self,
            container: str,
            region: str = None,
            secure: bool = True) -> None:
        super().__init__(container, region, secure)
        try:
            self.client = Minio(
                env,
                access_key=self.access_key,
                secret_key=self.secret_key,
                region=self.region,
                secure=self.secure
            )
        except Exception as e:
            err = StorageError(e)
            log.exception(f'MinIO Exception [init]: {err}')
            raise err

    def object_exists(self, key: Key) -> bool:
        prefix = key.rsplit('/', 1)[-1] if '/' in key else None
        return key in self.client.list_objects(self.container, prefix)

    def container_exists(self) -> bool:
        return self.client.bucket_exists(self.container)

    def create_container(self) -> bool:
        self.client.make_bucket(self.container)

    def list_objects(
            self,
            prefix: PrefixPath = None,
            recursive: bool = False) -> List[str]:
        return self.client.list_objects(self.container, prefix, recursive)

    def put_object(self, key: Key, data: JSONish) -> str:
        data = BytesIO(data)
        return self.client.put_object(self.container, key, data)

    # TODO: Fix this thing, set up a ObjectInfo structure that will work between all storage
    # Likely need an Object option too... with the data. It'll need to be
    # compatible with JSONish
    def stat_object(self, key: str) -> ObjectInfo:
        data = self.client.stat_object(self.container, key)
        object_type = ObjectType.DIRECTORY if data.is_dir else ObjectType.FILE
        info = ObjectInfo(
            data.bucket_name,
            data.content_type,
            object_type,
            data.etag,
            data.is_delete_marker,
            data.is_latest,
            data.last_modified,
            data.metadata)
        info.container = data.bucket_name
        info.content_type = data.content_type

        return self.client.stat_object(self.container, key).__dict__
