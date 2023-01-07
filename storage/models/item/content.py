import mimetypes
from enum import Enum
from hashlib import sha256
from typing import List, Optional

import magic
from hashid import HashID, HashInfo
from pydantic import BaseModel, PositiveInt, StrictBytes, StrictStr

from storage.models.item.data import ObjectData
from storage.models.item.encryption import EncryptionAlgorithm

# from storage.models.item.paths import ObjectPath
from storage.models.item.size import SizeInfo
from storage.models.item.types import ItemType


class CompressionAlgorithm(str, Enum):
    LZ4 = "LZ4"
    GZIP = "GZIP"


class TypeDetection(str, Enum):
    magic = "magic"
    extension = "extension"


class ModelContentInfo(BaseModel):
    size: SizeInfo  # Size of data in bytes or all items in directory
    item_type: ItemType  # File or directory
    compression: Optional[CompressionAlgorithm] = None
    encryption: Optional[EncryptionAlgorithm] = None


class DirectoryContentInfo(ModelContentInfo):
    item_type: ItemType = ItemType.DIRECTORY
    num_items: PositiveInt = 0  # Number of items in directory


class TypeSignature(BaseModel):
    mime: StrictStr = "application/octet-stream"

    # @classmethod
    # def from_path(cls, name: ObjectPath) -> "TypeSignature":
    #     mime = None
    #     try:
    #         mime, _ = mimetypes.guess_type(name)
    #     except Exception:
    #         pass
    #     return cls(mime=mime) if mime else cls()

    @classmethod
    def from_data(cls, buffer: ObjectData) -> "TypeSignature":
        mime = None
        try:
            mime = magic.from_buffer(buffer.__root__, mime=True)
            mime = str(mime)
        except Exception:
            pass
        return cls(mime=mime) if mime else cls()

    @classmethod
    def validate(cls, v: str) -> "TypeSignature":
        # Check that v in MIME type database
        if v not in mimetypes.types_map.values():
            raise ValueError("Invalid MIME type")
        return cls(mime=v)


class HashSignature(BaseModel):
    algorithm: StrictStr = "SHA256"
    signature: StrictBytes

    @classmethod
    def from_data(cls, buffer: ObjectData) -> "HashSignature":
        signature = sha256(buffer.__root__).digest()
        return cls(signature=signature)

    @classmethod
    def validate(cls, v: bytes) -> "HashSignature":
        hashes: List[HashInfo] = list(HashID().identifyHash(v))
        hashes = [item.name for item in hashes if not item.extended]
        if "SHA256" not in hashes:
            raise ValueError("Invalid hash")
        return cls(signature=v)


class ObjectContentInfo(ModelContentInfo):
    item_type: ItemType = ItemType.FILE
    mime_type: TypeSignature  # MIME type for content
    signature: HashSignature  # Hash for integrity

    @classmethod
    def from_data(cls, data: ObjectData) -> "ObjectContentInfo":
        size = SizeInfo.from_data(data)
        mime_type = TypeSignature.from_data(data)
        signature = HashSignature.from_data(data)
        return cls(size=size, mime_type=mime_type, signature=signature)
