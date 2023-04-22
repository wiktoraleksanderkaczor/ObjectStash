"""Custom UUID type for Pioneer.""" ""
from typing import Optional
from uuid import uuid4

from pydantic.types import UUID4


class UniqueID(UUID4):
    def __init__(self, value: Optional[str] = None):
        super().__init__(value or uuid4().hex)

    def json(self):
        return self.hex

    @classmethod
    def from_json(cls, value):
        return UUID4(value)

    @classmethod
    def random(cls):
        return cls(uuid4().hex)
