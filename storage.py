import json
from ctypes import sizeof
from ensurepip import version
from enum import Enum
from importlib.metadata import metadata
from io import BytesIO
from typing import Any, Dict, Iterable, List, Mapping, Union

from minio import Minio
from pydantic import Protocol

from clients.local_client import LocalCLient
from clients.minio_client import MinioClient
from exceptions import StorageError

from .env import env
from .logger import log
from .validation import JSONish, Key, MergeIndex, MergeStrategy, PrefixPath


class Capability(str, Enum):
    BASIC = 'BASIC'
    STREAMS = 'STREAMS'
    APPENDS = 'APPENDS'


class MergeMode(str, Enum):
    UPDATE = 'UPDATE'
    ADDITIVE = 'ADDITIVE'
    SUBTRACT = 'SUBTRACT'
    INTERSECT = 'INTERSECT'  # If value in both sides


class ObjectType(str, Enum):
    DIRECTORY = 'DIRECTORY'
    FILE = "FILE"


class Owner:
    def __init__(self, name: str, identifier: str) -> None:
        self.name = name
        self.identifier = identifier


class Version:
    def __init__(self, hashed: str, is_latest: bool, version: str) -> None:
        self.hashed = hashed
        self.is_latest = is_latest
        self.version = version


class Metadata:
    def __init__(self, object_type: ObjectType, metadata, size) -> None:
        self.object_type = object_type
        self.metadata = metadata
        self.size = size


class ObjectInfo:
    def __init__(
            self,
            container: str,
            content_type: str,
            object_type: ObjectType,
            hashed: str,
            deleted: bool,
            is_latest: bool,
            last_modified: str,
            size: str,
            version: str,
            storage_class: str = None,
    ) -> None:
        self.container = container
        self.content_type = content_type
        self.object_type = object_type
        self.hashed = hashed
        self.deleted = deleted
        self.latest = is_latest
        self.last_modified = last_modified


# Handling singular and multiple object operations is done by calling the singular function multiple times by default
# If client has appropriate efficient functions, that can be called instead
# At a minimum, to implement the class, one requires;
# - all singular operations
# - all multiple operations without a singular alternative


class StorageClient(Protocol):
    client_name: str
    capabilities: List[Capability]

    def __init__(
            self,
            container: str,
            region: str = None,
            secure: bool = True):
        self.client = None
        self.container = container
        self.region = region
        self.secure = secure
        self.access_key: str = env['STORAGE']['ACCESS_KEY']
        self.secret_key: str = env['STORAGE']['SECRET_KEY']

    # REQUIRED:

    def container_exists(self) -> bool:
        ...

    def create_container(self) -> bool:
        ...

    def list_objects(
            self,
            prefix: str = PrefixPath,
            recursive: bool = None) -> List[Key]:
        ...

    def get_object(self, key: Key) -> JSONish:
        ...

    def put_object(self, key: Key, data: JSONish) -> Key:
        ...

    def stat_object(self, key: str) -> Dict[str, Any]:
        ...

    def remove_object(self, key: str) -> bool:
        ...

    # OPTIONAL:

    def get_objects(self, keys: List[Key]) -> List[JSONish]:
        return [self.get_object(key) for key in keys]

    def put_objects(
            self, keys: List[Key],
            data: List[JSONish]) -> List[Key]:
        return [self.put_object(key, item) for key, item in zip(keys, data)]

    def get_objects(self, keys: List[Key]) -> List[JSONish]:
        return [self.get_object(key) for key in keys]

    def stat_objects(self, keys: List[Key]) -> List[Dict[str, Any]]:
        return [self.stat_object(key) for key in keys]

    def remove_objects(self, keys: List[Key]) -> List[bool]:
        return [self.remove_object(key) for key in keys]

    def object_exists(self, key: Key) -> bool:
        prefix, key = key.rsplit('/', 1) if '/' in key else None, key
        return key in self.list_objects(prefix)

    def merge_object(
            self, key: Key, data: JSONish,
            index: MergeIndex = None, merge: MergeStrategy = None,
            mode: MergeMode = MergeMode.UPDATE) -> str:
        old = self.get_object(key)
        new = self._merge_mapping(old, data, index, merge, mode)
        return self.put_object(key, new)

    # INTERNAL:

    def _merge_value(
            self,
            old: Any,
            new: Any,
            mode: MergeMode = MergeMode.UPDATE) -> Any:
        if new is None:
            return old

        if mode == MergeMode.UPDATE:
            return new
        elif mode == MergeMode.ADDITIVE:
            return old + new
        elif mode == MergeMode.SUBTRACT:
            return old - new

    # TODO: Merging for iterables and with indexes, also strings
    # Might need option for multiple indexes...?
    def _merge_iterable(
            self,
            old: Iterable,
            new: Iterable,
            index: int,
            mode: MergeMode = MergeMode.UPDATE) -> List[Any]:
        if new is None:
            return old

        if mode == MergeMode.ADDITIVE:
            return old[:index] + new + old[index:]
        elif mode == MergeMode.SUBTRACT:
            return [item for item in old if item not in new]
        elif mode == MergeMode.UPDATE:
            return new

    def _merge_mapping(self, old: JSONish,
                       new: JSONish,
                       index: MergeIndex = None,
                       merge: MergeStrategy = None,
                       mode=MergeMode.UPDATE) -> JSONish:
        if not new:
            return old
        if not index:
            index = {}
        if not merge:
            merge = {}

        for k, v in old.items():
            if isinstance(v, Mapping):
                new[k] = self._merge_mapping(
                    v,
                    new.get(k, {}),
                    index.get(k, {}),
                    merge.get(k, {}),
                    merge.get(k, mode))
            elif isinstance(v, Iterable):
                new[k] = self._merge_iterable(
                    v,
                    new.get(k, []),
                    index.get(k, len(v)),
                    merge.get(k, mode))
            else:
                new[k] = self._merge_value(
                    new.get(k, None),
                    v,
                    merge.get(k, mode))
        return new


STORAGE_CLIENTS = {
    'Local': LocalCLient,
    'MinIO': MinioClient
}
storage: StorageClient = STORAGE_CLIENTS.get(
    env['STORAGE']['CLIENT'], MinioClient)
