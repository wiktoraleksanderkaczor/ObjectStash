from datetime import datetime
from enum import Enum
from typing import Dict, List
from uuid import uuid4

from pydantic import BaseModel


class Group(BaseModel):
    identifier: str = uuid4().hex
    name: str


class User(BaseModel):
    identifier: str = uuid4().hex
    name: str
    membership: List[Group]


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
    container: str
    storage_class: StorageClass


class PermissionFlags(BaseModel):
    read: bool
    write: bool
    execute: bool
    # list


class BytesSizeInfo(BaseModel):
    raw_bytes: int
    compressed_bytes: int = None


class ContentInfo(BaseModel):
    extension: str  # Content type for content
    size: BytesSizeInfo  # Size of data
    signature: str  # Hash for integrity
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


class ObjectInfo(BaseModel):
    uuid: str = uuid4().hex
    content: ContentInfo
    storage: StorageInfo
    ownership: OwnershipInfo
    permissions: PermissionInfo
    version: VersionInfo
