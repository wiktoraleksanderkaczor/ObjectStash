import mimetypes
from enum import Enum
from hashlib import sha256
from typing import Optional

import magic
from pydantic import BaseModel, PositiveInt, StrictBytes, StrictStr

from config.env import env
from storage.models.item.data import ObjectData
from storage.models.item.encryption import EncryptionAlgorithm
from storage.models.item.paths import ObjectPath
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


class ContainerContentInfo(ModelContentInfo):
    pass


class DirectoryContentInfo(ModelContentInfo):
    num_items: PositiveInt = 0  # Number of items in directory


class ObjectContentInfo(ModelContentInfo):
    mime_type: StrictStr  # Content type for content
    signature: StrictBytes  # Hash for integrity

    @classmethod
    def from_object(cls, name: "ObjectPath", data: "ObjectData") -> "ObjectContentInfo":
        path = str(name)
        buffer = data.__root__

        mime = "application/octet-stream"
        try:
            if env.objects.mime_method == TypeDetection.magic:
                mime = magic.from_buffer(buffer, mime=True)
                mime = str(mime)
            elif env.objects.mime_method == TypeDetection.extension:
                guess, _ = mimetypes.guess_type(path)
                mime = guess if guess else mime
        except Exception:
            pass

        signature = sha256(buffer).digest()
        item_type = ItemType.FILE
        size = SizeInfo(raw_bytes=len(buffer))

        return cls(mime_type=mime, signature=signature, item_type=item_type, size=size)
