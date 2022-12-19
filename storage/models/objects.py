import pickle
from datetime import datetime
from enum import Enum
from hashlib import sha256
from pathlib import PurePosixPath as ObjectID
from typing import Dict, List, Optional
from uuid import uuid4

import magic
from pydantic import UUID4, BaseModel, Field, PositiveInt, StrictBytes, StrictStr

from auth.models.group import Group
from auth.models.user import User
from config.env import env
from database.models.objects import JSON


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
    # container: StrictStr  # What is this?
    storage_class: StorageClass = StorageClass.HOT


class PermissionFlags(BaseModel):
    read: bool = True
    write: bool = True
    execute: bool = False
    # list


class SizeInfo(BaseModel):
    raw_bytes: PositiveInt = 0
    compressed_bytes: Optional[PositiveInt] = None


class ContentInfo(BaseModel):
    mime_type: StrictStr  # Content type for content
    size: SizeInfo  # Size of data in bytes
    signature: StrictBytes  # Hash for integrity
    compression: Optional[CompressionAlgorithm] = None
    encryption: Optional[EncryptionAlgorithm] = None

    @classmethod
    def from_bytes(cls, data: StrictBytes) -> "ContentInfo":
        try:
            mime = magic.from_buffer(data, mime=True)
        except Exception:
            mime = "application/octet-stream"
        size = SizeInfo(raw_bytes=len(data))
        signature = sha256(data).digest()

        return cls(mime_type=mime, size=size, signature=signature)


class PermissionInfo(BaseModel):
    mapping: Dict[str, PermissionFlags] = {env.cluster.user.uuid.hex: PermissionFlags()}  # UUID to permissions


class OwnershipInfo(BaseModel):
    owner: User = env.cluster.user
    group: Group = env.cluster.group


class ModificationInfo(BaseModel):
    modified: datetime = Field(default_factory=datetime.utcnow)
    created: datetime = Field(default_factory=datetime.utcnow)
    accessed: datetime = Field(default_factory=datetime.utcnow)


class VersionInfo(BaseModel):
    is_deleted: bool = False
    is_latest: bool = True
    when: ModificationInfo = ModificationInfo()


class ObjectInfo(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid4)
    content: ContentInfo
    storage: StorageInfo = StorageInfo()
    ownership: OwnershipInfo = OwnershipInfo()
    permissions: PermissionInfo = PermissionInfo()
    version: VersionInfo = VersionInfo()
    metadata: Metadata = Metadata()

    @classmethod
    def from_bytes(cls, data: StrictBytes) -> "ObjectInfo":
        content_info = ContentInfo.from_bytes(data)
        return cls(content=content_info)


class Object(BaseModel):
    name: ObjectID
    info: ObjectInfo
    data: StrictBytes

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> "Object":
        key = ObjectID(name)
        dumped = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        info = ObjectInfo.from_bytes(dumped)
        return cls(info=info, name=key, data=dumped)

    @classmethod
    def from_json(cls, name: str, data: JSON) -> "Object":
        return cls.from_dict(name, data.dict())

    @classmethod
    def from_basemodel(cls, name: str, data: BaseModel) -> "Object":
        return cls.from_dict(name, data.dict())
