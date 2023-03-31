"""Custom UUID type for Pioneer.""" ""
from uuid import uuid4

from pydantic.types import UUID4


class PioneerUUID(UUID4):
    def json(self):
        return self.hex

    @classmethod
    def from_json(cls, value):
        return UUID4(value)

    @classmethod
    def random(cls):
        return cls(uuid4().hex)
