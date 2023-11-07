"""
StorageKey is a model that represents a path to a file or directory in a storage.
"""
import os.path
import re
from typing import List, Pattern, Union

from pydantic import BaseModel

from storage.models.client.key import StorageClientKey

VALID_PATH: Pattern = re.compile(r"^[a-zA-Z0-9_\-\.\/]+$")


class StoragePath(BaseModel):
    """
    StoragePath is a model that represents a path to a file or directory in a storage.
    No wildcard, regex or unsafe append, that's handled by the operating system
    """

    path: str

    @classmethod
    def validate(cls, value: "StoragePath") -> "StoragePath":
        if not value:
            raise ValueError("StoragePath cannot be empty")
        if not isinstance(value, StoragePath):
            raise ValueError("StoragePath is invalid")
        if VALID_PATH.match(value.path) is None:
            raise ValueError("StoragePath contains illegal characters")

        return value

    def join(self, path: Union[str, "StoragePath"]) -> "StoragePath":
        if isinstance(path, StoragePath):
            path = str(path)
        return StoragePath(path=os.path.join(self.path, path))

    def prefix(self, prefix: Union[str, "StoragePath"]) -> "StoragePath":
        if isinstance(prefix, StoragePath):
            return prefix.join(self.path)
        return StoragePath(path=prefix + self.path)

    def postfix(self, suffix: Union[str, "StoragePath"]):
        if isinstance(suffix, StoragePath):
            return self.join(suffix)
        return StoragePath(path=self.path + suffix)

    @property
    def parent(self) -> "StoragePath":
        return StoragePath(path=os.path.dirname(self.path))

    @property
    def parts(self) -> List[str]:
        return self.path.split("/")

    @property
    def suffix(self) -> str:
        return os.path.splitext(self.path)[1]

    @property
    def suffixes(self) -> List[str]:
        return self.name.split(".")[1:]

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    def __str__(self):
        return self.path


class StorageKey(BaseModel):
    storage: StorageClientKey
    path: StoragePath

    def __hash__(self):
        return hash(f"{self.path}@{self.storage}")

    def join(self, path: Union[str, StoragePath]):
        return StorageKey(storage=self.storage, path=self.path.join(path))


if __name__ == "__main__":
    a: StoragePath = StoragePath(path="test")
    b = a.join("test")
    print(str(b))
    import json

    print(json.dumps(b))
    # StoragePath()
