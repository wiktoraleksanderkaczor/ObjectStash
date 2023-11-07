"""
Header model
"""
from typing import Dict, Tuple

from pydantic import BaseModel
from typing_extensions import Self

from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey


class Header(BaseModel):
    key: StorageKey
    objects: Dict[StorageKey, Object]

    def update(self: Self, obj: Object) -> None:
        self.objects[obj.key] = obj

    def create_file(self: Self) -> Tuple[Object, FileData]:
        encoded = self.json().encode()
        obj, data = Object.create_file(self.key, encoded)
        return obj, data

    @classmethod
    def validate(cls, value: "Header") -> "Header":
        if any(item.key.storage for item in value.objects.values()):
            raise ValueError("Header cannot contain folders")
        return value
