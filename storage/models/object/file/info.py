"""Content information for items."""
from enum import Enum
from hashlib import sha256
from typing import List, Optional

import magic
from hashid import HashID, HashInfo
from magic import MagicException
from pydantic import ByteSize, StrictStr

from datamodel.data.model import Data
from storage.models.object.file.data import FileData
from storage.models.object.file.encryption import EncryptionAlgorithm


class CompressionAlgorithm(str, Enum):
    LZ4 = "LZ4"
    GZIP = "GZIP"


class TypeDetection(str, Enum):
    MAGIC = "magic"
    EXTENSION = "extension"


class SizeInfo(Data):
    raw_bytes: ByteSize = ByteSize(0)
    compressed_bytes: Optional[ByteSize] = None

    @classmethod
    def from_buffer(cls, buffer: FileData) -> "SizeInfo":
        return cls(raw_bytes=ByteSize(len(buffer)))


class TypeSignature(Data):
    mime: StrictStr = "application/octet-stream"

    @classmethod
    def from_buffer(cls, buffer: FileData) -> "TypeSignature":
        mime = None
        try:
            mime = magic.from_buffer(buffer, mime=True)
            mime = str(mime)
        except MagicException:
            pass
        return cls(mime=mime) if mime else cls()

    @classmethod
    def validate(cls, value: "TypeSignature") -> "TypeSignature":
        # Check that v in MIME type database
        if not value.mime:  # not in mimetypes.types_map.values():
            raise ValueError("Unknown or invalid MIME type")
        return value


class HashSignature(Data):
    algorithm: StrictStr = "SHA-256"
    signature: str

    @classmethod
    def from_buffer(cls, buffer: FileData) -> "HashSignature":
        signature = sha256(buffer).hexdigest()
        return cls(signature=signature)

    @classmethod
    def validate(cls, value: "HashSignature") -> "HashSignature":
        hashes: List[HashInfo] = list(HashID().identifyHash(value.signature))
        hashes = [item.name for item in hashes if not item.extended]
        if "SHA-256" not in hashes:
            raise ValueError("Invalid hash")
        return value


class ObjectInfo(Data):
    size: SizeInfo  # Size of data in bytes or all items in directory
    mime_type: TypeSignature  # MIME type for content
    signature: HashSignature  # Hash for integrity
    compression: Optional[CompressionAlgorithm] = None
    encryption: Optional[EncryptionAlgorithm] = None

    @classmethod
    def from_buffer(cls, buffer: FileData) -> "ObjectInfo":
        size = SizeInfo.from_buffer(buffer)
        mime_type = TypeSignature.from_buffer(buffer)
        signature = HashSignature.from_buffer(buffer)
        return cls(size=size, mime_type=mime_type, signature=signature)
