from datetime import datetime
from enum import Enum
from pathlib import PurePosixPath as ObjectID
from typing import Dict, List
from uuid import uuid4

from auth.models.group import Group
from auth.models.user import User
from pydantic import UUID4, BaseModel, Field, PositiveInt, StrictBytes, StrictStr


class Metadata(BaseModel):
    tags: List[str] = []


class StorageClass(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    GLACIER = "GLACIER"


class CompressionAlgorithm(str, Enum):
    LZ4 = "LZ4"
    GZIP = "GZIP"


class EncryptionAlgorithm(str, Enum):
    AES256 = "AES256"


class StorageInfo(BaseModel):
    container: StrictStr
    storage_class: StorageClass


class PermissionFlags(BaseModel):
    read: bool
    write: bool
    execute: bool
    # list


class SizeInfo(BaseModel):
    raw_bytes: PositiveInt = 0
    compressed_bytes: PositiveInt = 0


class ContentInfo(BaseModel):
    extension: StrictStr  # Content type for content
    size: SizeInfo  # Size of data in bytes
    signature: StrictBytes  # Hash for integrity
    compression: CompressionAlgorithm
    encryption: EncryptionAlgorithm


class PermissionInfo(BaseModel):
    mapping: Dict[str, PermissionFlags]  # UUID to permissions
    default: PermissionFlags


class OwnershipInfo(BaseModel):
    owner: User
    group: Group


class ModificationInfo(BaseModel):
    modified: datetime
    created: datetime
    accessed: datetime


class VersionInfo(BaseModel):
    is_deleted: bool
    is_latest: bool
    when: ModificationInfo


class ObjectInfo(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid4)
    content: ContentInfo
    storage: StorageInfo
    ownership: OwnershipInfo
    permissions: PermissionInfo
    version: VersionInfo
    metadata: Metadata


class ContentData(BaseModel):
    data: StrictBytes


class Object(BaseModel):
    name: ObjectID
    info: ObjectInfo
    data: ContentData
