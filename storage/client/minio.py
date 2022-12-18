from typing import List

from minio import Minio

from config.env import env
from config.logger import log
from storage.models.capabilities import Capability
from storage.models.client import StorageClient
from storage.models.medium import Medium
from storage.models.objects import Object, ObjectID, ObjectInfo


class MinIOClient(StorageClient):
    CLIENT_NAME: str = "MinIO"
    CAPABILITIES: List[Capability] = [Capability.BASIC]
    MEDIUM: str = Medium.DISTRIBUTED

    def __init__(self, container: str, region: str = None, secure: bool = True) -> None:
        super().__init__(container, region, secure)
        try:
            self.client = Minio(
                env, access_key=self.access_key, secret_key=self.secret_key, region=self.region, secure=self.secure
            )
        except Exception as e:
            log.exception(f"MinIO Exception [init]: {e}")
            raise e

    def container_exists(self) -> bool:
        return self.client.bucket_exists(self.container)

    def create_container(self) -> bool:
        self.client.make_bucket(self.container)

    def list_objects(self, prefix: ObjectID, recursive: bool = False) -> List[ObjectID]:
        return self.client.list_objects(self.container, prefix, recursive)

    def get_object(self, key: ObjectID) -> Object:
        return self.client.get_object(self.container, key)

    def put_object(self, key: ObjectID, obj: Object) -> bool:
        return self.client.put_object(self.container, key, obj)

    def stat_object(self, key: ObjectID) -> ObjectInfo:
        return self.client.stat_object(self.container, key).__dict__

    def remove_object(self, key: ObjectID) -> bool:
        return self.client.remove_object(self.container, key)
