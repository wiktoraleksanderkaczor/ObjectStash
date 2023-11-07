"""MinIO Storage Client"""
from io import BytesIO
from typing import Union

from minio import Minio
from urllib3.response import BaseHTTPResponse as S3Response

from storage.models.client.medium import Medium
from storage.models.object.file.data import FileData
from storage.models.object.models import File, Object
from storage.models.object.path import StorageKey
from storage.superclass.client import BaseStorageClient


class S3Client(BaseStorageClient):
    def __init__(
        self,
        bucket: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool,
        region: Union[str, None] = None,
    ) -> None:
        super().__init__()
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            session_token=None,
            region=region,
        )
        self.bucket = bucket

    @property
    def medium(self) -> Medium:
        return Medium.REMOTE

    def get(self, key: StorageKey) -> FileData:
        resp: S3Response = self.client.get_object(self.bucket, str(key.path))
        return FileData(__root__=resp.read())

    # Creating empty folders possible in '._head' only
    def put(self, obj: Object, data: FileData) -> None:
        if not isinstance(obj.item, File):
            raise ValueError("Object is not a file")

        content_type = obj.item.content.mime_type.mime
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=str(obj.key.path),
            data=BytesIO(data.__root__),
            length=len(data.__root__),
            content_type=content_type,
        )
        super().put(obj, data)

    def remove(self, key: StorageKey) -> None:
        self.client.remove_object(self.bucket, str(key.path))
