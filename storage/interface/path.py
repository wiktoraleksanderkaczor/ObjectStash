from abc import abstractmethod
from pathlib import PurePosixPath

from storage.models.client.key import StorageClientKey


class StorageKey:
    # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
    # http://davis.lbl.gov/Manuals/PYTHON-2.4.3/lib/pickle-inst.html
    @abstractmethod
    def __init__(self, storage: StorageClientKey, path: PurePosixPath):
        self.storage = storage
        self.path = path
        ...

    @abstractmethod
    def __repr__(self):
        ...

    @abstractmethod
    def __str__(self):
        ...

    @abstractmethod
    def __new__(cls, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        ...

    # NOTE: Cannot do this, it will operate on current object as if PurePosixPath... and return one too.
    # Only called when not in current object, error when no such attr
    # def __getattribute__(self, attr):
    #     return getattr(self.path, attr)

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

    # @classmethod
    # def validate(cls, storage: StorageClientKey, path: StorageKey):
    #     try:
    #         client = StorageClient.clients[storage]
    #         exists = client.exists(path)
    #         if exists:
    #             stat = client.stat(path)
    #             if stat.content.item_type == ItemType.DIRECTORY:
    #                 if path.suffixes:
    #                     raise ValueError("Not a directory")
    #             elif stat.content.item_type == ItemType.FILE:
    #                 if not path.suffixes:
    #                     raise ValueError("Not a file")
    #     except Exception as e:
    #         raise ValueError(f"Invalid StorageKey: {e}")
    #     return cls(storage=storage, path=path)

    @abstractmethod
    def __getstate__(self):
        ...

    @abstractmethod
    def __setstate__(self, state):
        ...


# Should I override the class for validation of particular types like file or directory?
# Would this be good to be overriden in particular storage applications, like database wanting some special fields?
# Finally, duck typing should theoretically allow using this instead of StorageKey but needs validation
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
