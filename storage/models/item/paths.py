from pathlib import PurePosixPath

from storage.models.client.key import StorageClientKey
from storage.models.client.model import StorageClient
from storage.models.item.types import ItemType


class StorageKey:
    # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
    # http://davis.lbl.gov/Manuals/PYTHON-2.4.3/lib/pickle-inst.html

    # Do I need to pass whether it's a directory or file when it doesn't exist yet?
    def __init__(self, storage: StorageClientKey, path: PurePosixPath):
        self.storage = storage
        self.path = path
        try:
            self.__client = StorageClient.clients[storage]
        except KeyError:
            raise KeyError(f"'{storage}' not found in initialized storage clients")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.storage}://{str(self.path)})"

    def __str__(self):
        return f"{self.storage}://({self.path}"

    def __new__(cls, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        return object.__new__(cls)

    # NOTE: Cannot do this, it will operate on current object as if PurePosixPath... and return one too.
    # Only called when not in current object, error when no such attr
    # def __getattribute__(self, attr):
    #     return getattr(self.path, attr)

    def is_dir(self) -> bool:
        stat = self.__client.stat(self)
        if stat.content.item_type == ItemType.DIRECTORY:
            return True
        return False

    def is_file(self) -> bool:
        stat = self.__client.stat(self)
        if stat.content.item_type == ItemType.FILE:
            return True
        return False

    def exists(self) -> bool:
        try:
            self.__client.stat(self)
        except Exception:
            return False
        return True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        try:
            if not storage or not path:
                raise ValueError("Missing 'storage' or 'path'")
        except Exception as e:
            raise ValueError(f"Invalid StorageKey: {e}")
        return cls(storage=storage, path=path)

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
    #     except KeyError:
    #         raise KeyError(f"'{storage}' not found in initialized storage clients")
    #     except Exception as e:
    #         raise ValueError(f"Invalid StorageKey: {e}")
    #     return cls(storage=storage, path=path)


# Should I override the class for validation of particular types like file or directory?
# Would this be good to be overriden in particular storage applications, like database wanting some special fields?
# Finally, duck typing should theoretically allow using this instead of StorageKey but needs validation
class DirectoryPath(StorageKey):
    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_dir() and v.exists():
            raise ValueError("Not a directory")


class ObjectPath(StorageKey):
    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_file() and v.exists():
            raise ValueError(f"'{v}' is a directory")
