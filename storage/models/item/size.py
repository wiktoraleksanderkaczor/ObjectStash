from typing import Optional

from pydantic import BaseModel, PositiveInt


class SizeInfo(BaseModel):
    raw_bytes: PositiveInt = 0
    compressed_bytes: Optional[PositiveInt] = None
