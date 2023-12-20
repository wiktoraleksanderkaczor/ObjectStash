"""
This module contains the models for the items in the storage service.
"""
from typing import Tuple, Type, Union

from datamodel.data.model import Data
from storage.models.object.file.data import FileData
from storage.models.object.file.info import ObjectInfo
from storage.models.object.metadata import Metadata
from storage.models.object.path import StorageKey


class File(Data):
    content: ObjectInfo

    @classmethod
    def create(cls: Type["File"], raw: bytes) -> Tuple["File", "FileData"]:
        content = ObjectInfo.from_buffer(raw)
        return File(content=content), raw


class Folder(Data):
    num_items: int = 0


# class Device(Data):
#     pass


class Object(Data):
    key: StorageKey
    metadata: Metadata
    item: Union[File, Folder]  # , Device]

    @classmethod
    def create_file(cls: Type["Object"], key: StorageKey, raw: bytes) -> Tuple["Object", "FileData"]:
        file, data = File.create(raw)
        return (
            Object(
                key=key,
                metadata=Metadata(),
                item=file,
            ),
            data,
        )

    @classmethod
    def create_folder(cls: Type["Object"], key: StorageKey) -> "Object":
        return Object(
            key=key,
            metadata=Metadata(),
            item=Folder(),
        )

    def is_file(self) -> bool:
        return isinstance(self.item, File)

    def is_folder(self) -> bool:
        return isinstance(self.item, Folder)
