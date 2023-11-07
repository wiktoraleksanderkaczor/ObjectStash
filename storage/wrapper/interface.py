"""
Interface for storage wrapper.
"""
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Union

from network.superclass.wrapping import DistributedObjectProxy
from storage.interface.client import StorageClientInterface
from storage.models.client.info import StorageInfo
from storage.models.client.key import StorageClientKey
from storage.models.client.medium import Medium
from storage.models.object.file.info import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey, StoragePath


class StorageWrapper(DistributedObjectProxy, StorageClientInterface):
    RESERVED: List[StoragePath]

    def __init__(self, wrapped: StorageClientInterface):
        super().__init__(wrapped)
        self.__wrapped__: StorageClientInterface = wrapped  # typing fix
        self.RESERVED = self.__wrapped__.RESERVED  # pylint: disable=invalid-name

    def __repr__(self):
        # StorageWrapper:StorageClientInterface@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        return f"{self.__class__.__name__}:{repr(self.__wrapped__)}"

    def get(self, key: StorageKey) -> FileData:
        return self.__wrapped__.get(key)

    def put(self, obj: Object, data: FileData) -> None:
        return self.__wrapped__.put(obj, data)

    def remove(self, key: StorageKey) -> None:
        return self.__wrapped__.remove(key)

    def stat(self, key: StorageKey) -> Object:
        return self.__wrapped__.stat(key)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        return self.__wrapped__.list(prefix, recursive)

    def header(self, key: StorageKey) -> Dict[StorageKey, Object]:
        return self.__wrapped__.header(key)

    def update(self, obj: Object) -> None:
        return self.__wrapped__.update(obj)

    def exists(self, key: StorageKey) -> bool:
        return self.__wrapped__.exists(key)

    def __contains__(self, key: StorageKey) -> bool:
        return key in self.__wrapped__

    @property
    def __dict__(self):
        # Might be needed for more correct behavior later, unknown if properly writable
        # merged = {}
        # merged.update(super().__dict__)
        # merged.update(self.__wrapped__.__dict__)
        return self.__wrapped__.__dict__

    @property
    def name(self) -> StorageClientKey:
        return self.__wrapped__.name

    @property
    def info(self) -> StorageInfo:
        return self.__wrapped__.info

    @property
    def medium(self) -> Medium:
        return self.__wrapped__.medium

    @contextmanager
    def transact(self, key: Union[StorageKey, List[StorageKey]]) -> Generator[None, Any, Any]:
        self.__wrapped__.transact(key)
        yield
