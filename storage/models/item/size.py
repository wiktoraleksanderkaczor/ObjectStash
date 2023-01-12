from typing import Optional

from pydantic import BaseModel, ByteSize

from storage.models.item.models import ObjectData


class SizeInfo(BaseModel):
    raw_bytes: ByteSize = ByteSize(0)
    compressed_bytes: Optional[ByteSize] = None

    @classmethod
    def from_data(cls, data: ObjectData) -> "SizeInfo":
        return cls(raw_bytes=ByteSize(len(data.__root__)))
