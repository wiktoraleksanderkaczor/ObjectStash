"""
This module contains the models for the items in the storage service.
"""
from typing import Tuple, Type

from pydantic import BaseModel

from datamodel.unique import UniqueID
from storage.models.object.content import ObjectContentInfo, ObjectData
from storage.models.object.metadata import ObjectMetadata
from storage.models.object.path import StorageKey


class Object(BaseModel):
    uuid: UniqueID
    name: StorageKey
    content: ObjectContentInfo
    metadata: ObjectMetadata

    @classmethod
    def create(cls: Type["Object"], name: StorageKey, raw: bytes) -> Tuple["Object", "ObjectData"]:
        uuid = UniqueID()
        data = ObjectData(__root__=raw)
        content = ObjectContentInfo.from_data(data)
        metadata = ObjectMetadata()
        return Object(uuid=uuid, name=name, content=content, metadata=metadata), data
