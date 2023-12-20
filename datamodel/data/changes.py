"""
Change tracking for data objects.
"""
from typing import TYPE_CHECKING

from datamodel.data.view.nested import NestedData

if TYPE_CHECKING:
    from datamodel.data.model import Data


class ChangeTracker(NestedData):
    def __init__(self):
        super().__init__({})

    def apply(self, data: "Data") -> "Data":
        dumped = data.model_dump()
        for path, value in self:
            root = dumped
            for part in path[:-1]:
                root = root[part]
            root[path[-1]] = value
        return data.from_obj(dumped)

    def __bool__(self):
        return bool(self.data)
