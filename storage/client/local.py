"""Local storage client."""
import shutil
from pathlib import Path
from typing import List

from config.models.env import StorageConfig
from storage.models.client.medium import Medium
from storage.models.object.file.info import FileData
from storage.models.object.metadata import Metadata
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath
from storage.superclass.client import BaseStorageClient


class LocalClient(BaseStorageClient):
    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> FileData:
        with open(str(key.path), "rb") as handle:
            return FileData(__root__=handle.read())

    def stat(self, key: StorageKey) -> Object:
        path = self.meta.joinpath(str(key.path))
        return Object.parse_file(path)

    def put(self, obj: Object, data: FileData) -> None:
        # Define object and data paths
        meta = self.meta.joinpath(str(obj.name.path))
        path = Path(str(obj.name.path))
        # Write object to disk
        meta.parent.mkdir(parents=True, exist_ok=True)
        meta.touch(exist_ok=True)
        meta.write_bytes(obj.json().encode())
        # Create containing directory and write data to disk
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        path.write_bytes(data.__root__)

    def remove(self, key: StorageKey) -> None:
        obj = self.meta.joinpath(str(key.path))
        shutil.rmtree(obj)
        shutil.rmtree(str(key.path))

    def change(self, key: StorageKey, metadata: Metadata) -> None:
        path = self.meta.joinpath(str(key.path))
        path.unlink()
        path.touch(exist_ok=False)
        path.write_bytes(metadata.json().encode())

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        path = Path(str(prefix.path))
        glob = path.glob("*/**/*" if recursive else "*")
        files = [item for item in glob if item.is_file()]
        keys = [StorageKey(storage=self.name, path=StoragePath(str(item))) for item in files]
        return keys

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.meta = Path(".meta")
        self.meta.mkdir(parents=True, exist_ok=True)
