from abc import abstractmethod
from pathlib import PurePosixPath

from storage.models.client.key import StorageClientKey


class StorageKey:
    # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
    # http://davis.lbl.gov/Manuals/PYTHON-2.4.3/lib/pickle-inst.html
    @abstractmethod
    def __init__(self, storage: StorageClientKey, path: PurePosixPath):
        self.storage: StorageClientKey
        self.path: PurePosixPath
        ...

    @abstractmethod
    def __new__(cls, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        ...

    @abstractmethod
    def __repr__(self):
        ...

    @abstractmethod
    def __str__(self):
        ...

    @abstractmethod
    def is_dir(self) -> bool:
        ...

    @abstractmethod
    def is_file(self) -> bool:
        ...

    @abstractmethod
    def exists(self) -> bool:
        ...

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    @abstractmethod
    def validate(cls, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        ...

    @abstractmethod
    def __getstate__(self):
        ...

    @abstractmethod
    def __setstate__(self, state):
        ...


class DirectoryKey(StorageKey):
    @classmethod
    @abstractmethod
    def validate(cls, *args, **kwargs) -> "DirectoryKey":
        ...


class ObjectKey(StorageKey):
    @classmethod
    @abstractmethod
    def validate(cls, *args, **kwargs) -> "ObjectKey":
        ...
