"""Custom UUID type for Pioneer.""" ""
from typing import Optional
from uuid import UUID, uuid4


class UniqueID(UUID):
    def __init__(self, value: Optional[str] = None):
        super().__init__(hex=value, version=4)

    def json(self):
        return self.hex

    @property
    def hex(self):
        return str(self)

    @classmethod
    def from_json(cls, value):
        return cls(value)

    @classmethod
    def random(cls):
        return cls(uuid4().hex)
