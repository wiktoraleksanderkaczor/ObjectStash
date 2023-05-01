"""Local storage client."""
import shutil
from pathlib import Path
from typing import Iterable, List, Union

from xattr import xattr

from datamodel.data import JSON
from storage.models.client.medium import Medium
from storage.models.object.file.info import FileData
from storage.models.object.metadata import Metadata
from storage.models.object.models import File, Folder, Object
from storage.models.object.path import StorageKey, StoragePath
from storage.superclass.client import BaseStorageClient


# Passthrough permission changes to local filesystem using 'facls'
class LocalClient(BaseStorageClient):
    @property
    def medium(self) -> Medium:
        return Medium.LOCAL

    def get(self, key: StorageKey) -> FileData:
        with open(str(key.path), "rb") as handle:
            return FileData(__root__=handle.read())

    def stat(self, key: StorageKey) -> Object:
        attrs = xattr(str(key.path))

        def attr_to_fieldpath(attr: str):
            attr = attr.removeprefix("pioneer.")
            split = attr.split(".")
            parsed = [int(kv) if kv.isnumeric() else kv for kv in split]
            return parsed

        flattened = [(name, val) for name, val in attrs.items() if isinstance(name, str)]
        flattened = filter(lambda attr: attr[0].startswith("pioneer."), flattened)
        flattened = map(lambda attr: (attr_to_fieldpath(attr[0]), attr[1]), flattened)
        flattened = filter(lambda attr: bool(attr[1]), flattened)
        flattened = list(flattened)
        metajson = JSON.from_flattened(flattened)
        metadata = Metadata.parse_raw(metajson.json())
        item: Union[File, Folder]
        try:
            data = self.get(key)
            item, _ = File.create(data.__root__)
        except KeyError:
            item = Folder()
        return Object(name=key, metadata=metadata, item=item)

    def put(self, obj: Object, data: FileData) -> None:
        # Define object path
        path = Path(str(obj.name.path))
        # Write object to disk
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        path.write_bytes(data.__root__)
        # Set metadata
        self.change(obj.name, obj.metadata)

    def remove(self, key: StorageKey) -> None:
        shutil.rmtree(str(key.path))

    def change(self, key: StorageKey, metadata: Metadata) -> None:
        # Handles maps and iterables quite badly
        flattened = JSON.parse_obj(metadata.dict()).flatten()
        attrs = xattr(str(key.path))
        for name, value in flattened:
            if isinstance(name, Iterable):
                name = ".".join(name)
            name = "pioneer." + name
            attrs.set(name, value)
            # attrs.set(name, metadata.permissions.json().encode())

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        path = Path(str(prefix.path))
        glob = path.glob("*/**/*" if recursive else "*")
        files = [item for item in glob if item.is_file()]
        keys = [StorageKey(storage=self.name, path=StoragePath(str(item))) for item in files]
        return keys
