"""
Base class for storage clients.
"""
import json
from abc import abstractmethod
from typing import Dict, List

from storage.interface.client import StorageClientInterface
from storage.models.client.info import StorageInfo
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.object.file.data import FileData
from storage.models.object.metadata import Metadata
from storage.models.object.models import Folder, Object
from storage.models.object.path import StorageKey, StoragePath


class BaseStorageClient(StorageClientInterface):
    RESERVED = [
        StoragePath("._mount.json"),
        StoragePath("._info.json"),
        # StoragePath("._meta"),
        StoragePath("._header.json"),
    ]

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def get(self, key: StorageKey) -> FileData:
        ...

    @abstractmethod
    def put(self, obj: Object, data: FileData) -> None:
        ...

    @abstractmethod
    def remove(self, key: StorageKey) -> None:
        ...

    def stat(self, key: StorageKey) -> Object:
        header = self.head(key)
        return header[key]

    def change(self, key: StorageKey, metadata: Metadata) -> None:
        head_key = self._get_head_key(key)
        header = self.head(head_key)
        header[key].metadata = metadata
        encoded = json.dumps(header).encode()
        obj, data = Object.create_file(head_key, encoded)
        self.put(obj, data)

    # Might add depth limit parameter, decrease by 1 each recursive call
    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        header = self.head(prefix)
        items = list(header.keys())
        if recursive:
            folders = [k for k, v in header.items() if isinstance(v, Folder)]
            new = [self.list(folder, recursive) for folder in folders]
            items.extend(*new)
        return items

    def head(self, key: StorageKey) -> Dict[StorageKey, Object]:
        head_key = self._get_head_key(key)
        data = self.get(head_key)
        header = json.loads(data.__root__)
        return header

    def exists(self, key: StorageKey) -> bool:
        return key in self

    def __contains__(self, key: StorageKey) -> bool:
        try:
            self.stat(key)
        except KeyError:
            return False
        return True

    def _get_head_key(self, key: StorageKey):
        dir_path = key.path.parent if self.stat(key).is_file() else key.path
        dir_key = StorageKey(storage=self.name, path=dir_path)
        file_key = dir_key.join("._head.json")
        return file_key

    @property
    def name(self) -> StorageClientKey:
        return StorageClientKey(repr(self))

    @property
    def info(self) -> StorageInfo:
        key = StorageKey(storage=self.name, path=StoragePath("._info.json"))
        if key not in self:
            encoded = StorageInfo().json().encode()
            obj, data = Object.create_file(key, encoded)
            self.put(obj, data)
        decoded = self.get(key).to_text()
        return StorageInfo.parse_raw(decoded)

    @property
    def medium(self) -> Medium:
        ...

    # Hash for Pioneer client management set replacement
    def __hash__(self):
        return hash(self.name)

    # String representation for pathing
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.info.uuid}"
