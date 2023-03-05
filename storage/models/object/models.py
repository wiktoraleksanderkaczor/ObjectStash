"""
This module contains the models for the items in the storage service.
"""
from pathlib import PurePosixPath
from typing import Tuple, Type
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from storage.models.client.key import StorageClientKey
from storage.models.object.content import ObjectContentInfo, ObjectData
from storage.models.object.metadata import Metadata
from storage.models.object.ownership import OwnershipInfo
from storage.models.object.path import StorageKey
from storage.models.object.permissions import PermissionInfo
from storage.models.object.storage import StorageInfo
from storage.models.object.version import VersionInfo


class ItemModel(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid4)
    storage: StorageInfo = StorageInfo()
    ownership: OwnershipInfo = OwnershipInfo()
    permissions: PermissionInfo = PermissionInfo()
    metadata: Metadata = Metadata()
    version: VersionInfo = VersionInfo()


class Object(ItemModel):
    name: StorageKey
    content: ObjectContentInfo

    @classmethod
    def create(
        cls: Type["Object"], storage: StorageClientKey, path: PurePosixPath, raw: bytes
    ) -> Tuple["Object", "ObjectData"]:
        name = StorageKey(storage=storage, path=path)
        data = ObjectData(__root__=raw)
        content = ObjectContentInfo.from_data(data)
        return Object(name=name, content=content), data