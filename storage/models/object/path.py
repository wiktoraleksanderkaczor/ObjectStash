"""
StorageKey is a model that represents a path to a file or directory in a storage.
"""
import os.path

from pydantic import BaseModel

from storage.models.client.key import StorageClientKey


class StoragePath:
    """
    StoragePath is a model that represents a path to a file or directory in a storage.
    No wildcard, regex or unsafe append, that's handled by the operating system
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def joinpath(self, path: str) -> "StoragePath":
        new = os.path.join(self.path, path)
        return StoragePath(new)

    def prefix(self, prefix: str):
        return StoragePath(prefix + self.path)

    def postfix(self, suffix: str):
        return StoragePath(self.path + suffix)

    @property
    def parent(self):
        return os.path.dirname(self.path)

    @property
    def parts(self):
        return self.path.split("/")

    @property
    def suffix(self):
        return os.path.splitext(self.path)[1]

    @property
    def suffixes(self):
        return self.name.split(".")[1:]

    @property
    def name(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.path

    def json(self):
        return str(self)

    @classmethod
    def from_json(cls, value):
        return cls(value)


class StorageKey(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    storage: StorageClientKey
    path: StoragePath

    def __hash__(self):
        return hash(f"{self.path}@{self.storage}")

    def join(self, path: str):
        return StorageKey(storage=self.storage, path=self.path.joinpath(path))


if __name__ == "__main__":
    a: StoragePath = StoragePath(path="test")
    b = a.joinpath("test")
    print(str(b))
    import json

    print(json.dumps(b))
    # StoragePath()
