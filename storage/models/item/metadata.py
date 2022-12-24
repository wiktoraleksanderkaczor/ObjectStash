from typing import List

from pydantic import BaseModel


class Metadata(BaseModel):
    tags: List[str] = []
