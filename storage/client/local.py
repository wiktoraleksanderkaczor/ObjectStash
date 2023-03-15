"""Local storage client."""
import os
import shutil
from pathlib import Path, PurePosixPath
from typing import List

from config.models.env import StorageConfig
from storage.models.client.medium import Medium
from storage.models.object.content import ObjectData
from storage.models.object.models import Object, ObjectContentInfo
from storage.models.object.path import StorageKey
from storage.superclass.client import BaseStorageClient


class LocalClient(BaseStorageClient):
    def __init__(self, config: StorageConfig):
        super().__init__(config)

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> ObjectData:
        with open(key.path, "rb") as f:
            return ObjectData(__root__=f.read())

    def stat(self, key: StorageKey) -> Object:
        return Object(name=key, content=ObjectContentInfo.from_data(self.get(key)))

    def put(self, obj: Object, data: ObjectData) -> None:
        f = Path(obj.name.path)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch(exist_ok=True)
        f.write_bytes(data.__root__)

    def remove(self, key: StorageKey) -> None:
        shutil.rmtree(key.path)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        seed = os.listdir(prefix.path)
        dirs = [item for item in seed if os.path.isdir(item)]
        files = [item for item in seed if os.path.isfile(item)]
        if recursive:
            while dirs:
                new = os.listdir(dirs.pop())
                for item in new:
                    if os.path.isdir(item):
                        dirs.append(item)
                    else:
                        files.append(item)

        keys = [StorageKey(storage=self.name, path=PurePosixPath(item)) for item in files]
        return keys
