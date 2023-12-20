"""Local storage client."""
import shutil
from pathlib import Path

from storage.models.client.medium import Medium
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath
from storage.superclass.client import BaseStorageClient


# Passthrough permission changes to local filesystem using 'facls'
class LocalClient(BaseStorageClient):
    def __init__(self, root: StoragePath, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root = root

    def get(self, key: StorageKey) -> FileData:
        path = self.root.join(str(key.path))
        handle = Path(str(path))
        return handle.read_bytes()

    def put(self, obj: Object, data: FileData) -> None:
        # Resolve path
        path = self.root.join(str(obj.key.path))
        handle = Path(str(path))
        # Write object to disk
        handle.parent.mkdir(parents=True, exist_ok=True)
        handle.touch(exist_ok=True)
        handle.write_bytes(data)
        # Set header
        header = self.header(obj.key)
        header.objects[obj.key] = obj
        hobj, hdata = header.create_file()
        # Write header to disk
        hpath = self.root.join(str(hobj.key.path))
        hhandle = Path(str(hpath))
        hhandle.touch(exist_ok=True)
        hhandle.write_bytes(hdata)

    def remove(self, key: StorageKey) -> None:
        path = self.root.join(str(key.path))
        shutil.rmtree(str(path))

    @property
    def medium(self) -> Medium:
        return Medium.LOCAL
