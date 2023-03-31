"""Local storage client."""
import shutil
from pathlib import Path
from typing import List

from storage.models.client.medium import Medium
from storage.models.object.content import ObjectData
from storage.models.object.models import Object, ObjectContentInfo
from storage.models.object.path import StorageKey, StoragePath
from storage.superclass.client import BaseStorageClient


class LocalClient(BaseStorageClient):
    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> ObjectData:
        with open(str(key.path), "rb") as handle:
            return ObjectData(__root__=handle.read())

    def stat(self, key: StorageKey) -> Object:
        return Object(name=key, content=ObjectContentInfo.from_data(self.get(key)))

    def put(self, obj: Object, data: ObjectData) -> None:
        path = Path(str(obj.name.path))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        path.write_bytes(data.__root__)

    def remove(self, key: StorageKey) -> None:
        shutil.rmtree(str(key.path))

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        path = Path(str(prefix.path))
        glob = path.glob("**/*" if recursive else "*")
        files = [item for item in glob if item.is_file()]
        keys = [StorageKey(storage=self.name, path=StoragePath(str(item))) for item in files]
        return keys
