from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from storage.interface.path import DirectoryKey, ObjectKey
from storage.models.item.content import DirectoryContentInfo, ObjectContentInfo
from storage.models.item.metadata import Metadata
from storage.models.item.ownership import OwnershipInfo
from storage.models.item.permissions import PermissionInfo
from storage.models.item.storage import StorageInfo
from storage.models.item.version import VersionInfo


class ItemModel(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid4)
    storage: StorageInfo = StorageInfo()
    ownership: OwnershipInfo = OwnershipInfo()
    permissions: PermissionInfo = PermissionInfo()
    metadata: Metadata = Metadata()
    version: VersionInfo = VersionInfo()


class Directory(ItemModel):
    name: DirectoryKey
    content: DirectoryContentInfo


class Object(ItemModel):
    name: ObjectKey
    content: ObjectContentInfo
