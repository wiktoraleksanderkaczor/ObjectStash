"""
Header model
"""
from typing import Dict, Tuple

from typing_extensions import Self

from datamodel.data.model import Data
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey


class Header(Data):
    key: StorageKey
    objects: Dict[StorageKey, Object]

    def create_file(self: Self) -> Tuple[Object, FileData]:
        encoded = self.to_json().encode()
        obj, data = Object.create_file(self.key, encoded)
        return obj, data

    @classmethod
    def validate(cls, value: "Header") -> "Header":
        if any(item.key.storage for item in value.objects.values()):
            raise ValueError("Header cannot contain folders")
        return value
