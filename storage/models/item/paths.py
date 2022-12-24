from pathlib import PurePosixPath

from storage.models.client import StorageClient
from storage.models.item.types import ItemType


class StoragePath(PurePosixPath):
    def __init__(self, storage: StorageClient, value: str):
        self.wrapped = PurePosixPath(value)
        self.storage = storage

    def __new__(cls, storage: StorageClient, value: str) -> "StoragePath":
        return object.__new__(cls)

    # Only called when not in current object, error when no such attr
    def __getattribute__(self, attr):
        return getattr(self.wrapped, attr)

    def is_container(self) -> bool:
        stat = self.storage.head_item(self)
        if stat.content.item_type == ItemType.CONTAINER:
            return True
        return False

    def is_dir(self) -> bool:
        stat = self.storage.head_item(self)
        if stat.content.item_type == ItemType.DIRECTORY:
            return True
        return False

    def is_file(self) -> bool:
        stat = self.storage.head_item(self)
        if stat.content.item_type == ItemType.FILE:
            return True
        return False

    def exists(self) -> bool:
        try:
            self.storage.head_item(self)
        except Exception:
            return False
        return True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, storage: StorageClient, value: str) -> "StoragePath":
        try:
            PurePosixPath(value)
        except Exception as e:
            raise ValueError(f"Invalid StoragePath: {e}")
        return cls(storage, value)

    def __repr__(self):
        return f"StoragePath({super().__repr__()})"


class ContainerPath(StoragePath):
    def __repr__(self):
        return f"ContainerPath({super().__repr__()})"

    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_dir():
            raise ValueError("Not a container")


class DirectoryPath(StoragePath):
    def __repr__(self):
        return f"DirectoryPath({super().__repr__()})"

    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_dir():
            raise ValueError("Not a directory")


class ObjectPath(StoragePath):
    def __repr__(self):
        return f"ObjectPath({super().__repr__()})"

    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_file():
            raise ValueError(f"'{v}' is a directory")
