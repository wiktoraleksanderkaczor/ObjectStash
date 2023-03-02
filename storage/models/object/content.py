"""Content information for items."""
import mimetypes
from enum import Enum
from hashlib import sha256
from typing import List, Optional

import magic
from hashid import HashID, HashInfo
from magic import MagicException
from pydantic import BaseModel, ByteSize, StrictBytes, StrictStr

from storage.models.object.encryption import EncryptionAlgorithm


class ObjectData(BaseModel):
    __root__: StrictBytes


class CompressionAlgorithm(str, Enum):
    LZ4 = "LZ4"
    GZIP = "GZIP"


class TypeDetection(str, Enum):
    MAGIC = "magic"
    EXTENSION = "extension"


class SizeInfo(BaseModel):
    raw_bytes: ByteSize = ByteSize(0)
    compressed_bytes: Optional[ByteSize] = None

    @classmethod
    def from_data(cls, data: "ObjectData") -> "SizeInfo":
        return cls(raw_bytes=ByteSize(len(data.__root__)))


class TypeSignature(BaseModel):
    mime: StrictStr = "application/octet-stream"

    @classmethod
    def from_data(cls, buffer: "ObjectData") -> "TypeSignature":
        mime = None
        try:
            mime = magic.from_buffer(buffer.__root__, mime=True)
            mime = str(mime)
        except MagicException:
            pass
        return cls(mime=mime) if mime else cls()

    @classmethod
    def validate(cls, value: str) -> "TypeSignature":
        # Check that v in MIME type database
        if value not in mimetypes.types_map.values():
            raise ValueError("Invalid MIME type")
        return cls(mime=value)


class HashSignature(BaseModel):
    algorithm: StrictStr = "SHA256"
    signature: StrictBytes

    @classmethod
    def from_data(cls, buffer: "ObjectData") -> "HashSignature":
        signature = sha256(buffer.__root__).digest()
        return cls(signature=signature)

    @classmethod
    def validate(cls, value: bytes) -> "HashSignature":
        hashes: List[HashInfo] = list(HashID().identifyHash(value))
        hashes = [item.name for item in hashes if not item.extended]
        if "SHA256" not in hashes:
            raise ValueError("Invalid hash")
        return cls(signature=value)


class ObjectContentInfo(BaseModel):
    size: SizeInfo  # Size of data in bytes or all items in directory
    compression: Optional[CompressionAlgorithm] = None
    encryption: Optional[EncryptionAlgorithm] = None
    mime_type: TypeSignature  # MIME type for content
    signature: HashSignature  # Hash for integrity

    @classmethod
    def from_data(cls, data: "ObjectData") -> "ObjectContentInfo":
        size = SizeInfo.from_data(data)
        mime_type = TypeSignature.from_data(data)
        signature = HashSignature.from_data(data)
        return cls(size=size, mime_type=mime_type, signature=signature)
