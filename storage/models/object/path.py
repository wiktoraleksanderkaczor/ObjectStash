"""
StorageKey is a model that represents a path to a file or directory in a storage.
"""
from pathlib import PurePosixPath

from pydantic import BaseModel

from storage.models.client.key import StorageClientKey


class StorageKey(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    storage: StorageClientKey
    path: PurePosixPath

    def __hash__(self):
        return hash(f"{self.path}@{self.storage}")

    def join(self, path: str):
        return StorageKey(storage=self.storage, path=self.path.joinpath(path))
