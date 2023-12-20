"""
This module contains the implementation of an overlay wrapper for the storage client.
"""
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Union

from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class SafetyWrapper(StorageWrapper):
    def get(self, key: StorageKey) -> FileData:
        if key.path in self.__wrapped__.RESERVED:
            raise KeyError(f"Key '{key}' is reserved")
        return self.__wrapped__.get(key)

    def put(self, obj: Object, data: FileData) -> None:
        if obj.key.path in self.__wrapped__.RESERVED:
            raise KeyError(f"Key '{obj.key.path}' is reserved")
        return self.__wrapped__.put(obj, data)

    def remove(self, key: StorageKey) -> None:
        if key.path in self.__wrapped__.RESERVED:
            raise KeyError(f"Key '{key}' is reserved")
        return self.__wrapped__.remove(key)

    def stat(self, key: StorageKey) -> Object:
        if key.path in self.__wrapped__.RESERVED:
            raise KeyError(f"Key '{key}' is reserved")
        return self.__wrapped__.stat(key)

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        wrapped = self.__wrapped__.list(prefix, recursive=recursive)
        filtered = [key for key in wrapped if key.path not in self.__wrapped__.RESERVED]
        return filtered

    def header(self, key: StorageKey) -> Dict[StorageKey, Object]:
        if key.path in self.__wrapped__.RESERVED:
            raise KeyError(f"Key '{key}' is reserved")
        return self.__wrapped__.header(key)

    def exists(self, key: StorageKey) -> bool:
        if key.path in self.__wrapped__.RESERVED:
            return False
        return self.__wrapped__.exists(key)

    def __contains__(self, key: StorageKey) -> bool:
        if key.path in self.__wrapped__.RESERVED:
            return False
        return key in self.__wrapped__

    @contextmanager
    def transact(self, key: Union[StorageKey, List[StorageKey]]) -> Generator[None, Any, Any]:
        if isinstance(key, StorageKey):
            if key.path in self.__wrapped__.RESERVED:
                raise KeyError(f"Key '{key}' is reserved")
        elif isinstance(key, list):
            keys = [k for k in key if k.path in self.__wrapped__.RESERVED]
            if keys:
                raise KeyError(f"Keys '{keys}' are reserved")
        self.__wrapped__.transact(key)
        yield
