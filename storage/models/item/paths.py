import re
from pathlib import PurePosixPath
from typing import List, overload

from storage.models.client.key import StorageClientKey
from storage.models.client.model import StorageClient
from storage.models.item.types import ItemType

# NOTE: Look into https://stackoverflow.com/questions/45400284/understanding-init-subclass
# and maybe others like it, they're called hooks 

# Maybe even https://pypi.org/project/attrs/

# TODO: Implement own pure Path class with regex, path manipulation, validation, etc.
# TODO: Add various overload and property decordated methods like in PurePath from pathlib
# https://realpython.com/primer-on-python-decorators/#decorating-classes
# Also implement proper operators like Path("whatever") / "something" (or Path("whatever") + "something") and relevant 
# overloads
# https://docs.python.org/3/library/operator.html#mapping-operators-to-functions
# ...or find alternative pure path or path manipulation library
# Make it derive from string to be able to initialise it easy
# Alternatively, keep using the below but make any pathlib PurePath methods from getattribute only act on self.wrapped
# Also look into https://docs.pyfilesystem.org/en/latest/implementers.html ... maybe a pure version can be written?
class Path:
    def __init__(self, storage: StorageClientKey, path: str) -> None:
        self.storage = storage

        # Extract path root
        self.root = ""
        # Extract relative root from string using regex
        if match := 
        if match := RELATIVE_ROOT_REGEX.match(path):
            self.root = match.group("root")
            self.path = match.group("path")
        elif match := ABSOLUTE_ROOT_REGEX.match(path):
            self.root = match.group("root")
            self.path = match.group("path")
        else:
            self.path = path
        
        # Remove any leading or trailing slashes
        self.path = self.path.strip("/")

        # Remove any leading or trailing dots
        self.path = self.path.strip(".")

        self.path = path
        try:
            self.__client = StorageClient.clients[storage]
        except KeyError:
            raise KeyError(f"'{storage}' not found in initialized storage clients")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.storage}://{str(self.wrapped)})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.storage}://{str(self.wrapped)})"

    @classmethod
    def validate(cls, storage: StorageClientKey, path: str) -> "Path":
        try:
            v = cls(storage, path)
        except Exception as e:
            raise ValueError(f"Invalid StoragePath: {e}")
        return v

    def __truediv__(self, other: "Path") -> "Path":
        return Path(self.storage, self.path + "/" + other.path)

    def __hash__(self) -> int:
        return hash(self.__repr__())

    @property
    def parts(self) -> List[str]:
        return self.path.split("/")


class StoragePath(PurePosixPath):
    # TODO: Change path to FileUrl... sorta like {client.key}://{path}
    # How to still retain the whole joinpath bullshit? Maybe put it inside like;
    # self.path: PurePosixPath = PurePosixPath(value)
    def __init__(self, storage: StorageClientKey, path: PurePosixPath):
        self.storage = storage
        try:
            self.__client = StorageClient.clients[storage]
        except KeyError:
            raise KeyError(f"'{storage}' not found in initialized storage clients")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.storage}://{str(self.wrapped)})"

    def __new__(cls, storage: StorageClientKey, path: PurePosixPath) -> "StoragePath":
        return object.__new__(cls)

    # NOTE: Cannot do this, it will operate on current object as if PurePosixPath... and return one too.
    # Only called when not in current object, error when no such attr
    # def __getattribute__(self, attr):
    #     return getattr(self.wrapped, attr)

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

    def joinpath(self, *other: "StoragePath") -> "StoragePath":
        return StoragePath(self.storage, super().joinpath(*other))

    def __truediv__(self, other: "StoragePath") -> "StoragePath":
        return StoragePath(self.storage, super().__truediv__(other))



class StoragePath(PurePosixPath):
    @classmethod
    def validate(cls, value: PurePosixPath) -> "PurePosixPath":
        try:
            v = cls(value)
        except Exception as e:
            raise ValueError(f"Invalid StoragePath: {e}")
        return v

from pydantic import BaseModel

class Path(BaseModel):
    storage: StorageClientKey
    path: StoragePath

    @classmethod
    def validate(cls, storage: StorageClientKey, path: StoragePath):
        try:
            client = StorageClient.clients[storage]
            exists = client.exists(path)
            if exists:
                stat = client.stat(path)
                if stat.content.item_type == ItemType.DIRECTORY:
                    if path.suffixes:
                        raise ValueError("Not a directory")
                elif stat.content.item_type == ItemType.FILE:
                    if not path.suffixes:
                        raise ValueError("Not a file")
        except KeyError:
            raise KeyError(f"'{storage}' not found in initialized storage clients")
        except Exception as e:
            raise ValueError(f"Invalid StoragePath: {e}")
        return cls(storage=storage, path=path)

    def __str__(self):
        return f"{self.storage}://({self.path}"


class DirectoryPath(StoragePath):
    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_dir() and v.exists():
            raise ValueError("Not a directory")


class ObjectPath(StoragePath):
    @classmethod
    def validate(cls, *args, **kwargs):
        v = super().validate(*args, **kwargs)
        if not v.is_file() and v.exists():
            raise ValueError(f"'{v}' is a directory")
