from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from storage.models.item.content import ContainerContentInfo, DirectoryContentInfo, ObjectContentInfo
from storage.models.item.metadata import Metadata
from storage.models.item.ownership import OwnershipInfo
from storage.models.item.paths import ContainerPath, DirectoryPath, ObjectPath
from storage.models.item.permissions import PermissionInfo
from storage.models.item.storage import StorageInfo
from storage.models.item.version import VersionInfo


class ItemModel(BaseModel):
    uuid: UUID4 = Field(..., default_factory=uuid4)
    storage: StorageInfo = StorageInfo()
    ownership: OwnershipInfo = OwnershipInfo()
    permissions: PermissionInfo = PermissionInfo()
    metadata: Metadata = Metadata()
    version: VersionInfo = VersionInfo()


class Container(ItemModel):
    name: ContainerPath
    content: ContainerContentInfo


class Directory(ItemModel):
    name: DirectoryPath
    content: DirectoryContentInfo


class Object(ItemModel):
    name: ObjectPath
    content: ObjectContentInfo
