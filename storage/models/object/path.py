"""
StorageKey is a model that represents a path to a file or directory in a storage.
"""
from pathlib import PurePosixPath

from pydantic import BaseModel

from storage.models.client.key import StorageClientKey


class StorageKey(BaseModel):
    storage: StorageClientKey
    path: PurePosixPath

    def validate(self, storage: StorageClientKey, path: PurePosixPath) -> "StorageKey":
        return StorageKey(storage=storage, path=path)

    def join(self, path: str):
        return StorageKey(storage=self.storage, path=self.path.joinpath(path))
